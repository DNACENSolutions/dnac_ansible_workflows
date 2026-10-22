#!/usr/bin/env python3
"""Ansible Workflow Runner backend."""

import json
import os
import re
import shlex
import shutil
import signal
import ssl
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import secrets
import hashlib
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, Response, jsonify, render_template, request, session, redirect, url_for, g
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import safe_join

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"),
            static_folder=str(Path(__file__).parent / "static"))

# Credentials live outside the checkout; missing configuration fails closed.
AUTH_DIR = Path(os.environ.get("RUNNER_AUTH_DIR", Path.home() / ".config/catalystcenter-runner"))
app.config.update(
    RUNNER_USERS_FILE=os.environ.get("RUNNER_USERS_FILE", str(AUTH_DIR / "users.json")),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("RUNNER_COOKIE_SECURE", "true").lower() != "false",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    SESSION_REFRESH_EACH_REQUEST=False,
)
try:
    app.secret_key = os.environ.get("RUNNER_SECRET_KEY") or (AUTH_DIR / "secret.key").read_text().strip()
except OSError:
    app.secret_key = None
if app.secret_key and len(app.secret_key) < 32:
    app.secret_key = None
_auth_sessions = {}
_auth_attempts = {}
_auth_lock = threading.Lock()
_dummy_password_hash = generate_password_hash(secrets.token_urlsafe(32))
_roles = {"viewer": 0, "operator": 1, "admin": 2}
_read_endpoints = {"index", "job_detail", "api_workflows", "api_inventories", "api_environment",
                   "api_jobs", "api_job", "api_job_log", "api_stream", "saved_suites_list", "controller_profiles_list", "git_repositories_list"}
_operator_endpoints = {"api_device_interfaces", "api_host_port_assignments", "api_fs",
                       "api_read_file", "api_validate", "api_run", "api_run_suites",
                       "api_run_suite", "api_run_batch", "api_cancel", "api_cancel_suite",
                       "api_delete_job", "api_delete_suite", "api_rerun_job", "saved_suite_create", "saved_suite_update", "saved_suite_delete", "saved_suite_repo_catalog"}
_admin_endpoints = {"api_git_fetch", "api_write_file", "api_environment_create", "api_environment_setup", "saved_suite_reorder",
                    "controller_profile_save", "controller_profile_delete", "git_repository_remove"}

_profile_lock = threading.RLock()


def _profile_store():
    from cryptography.fernet import Fernet

    root = Path(app.config["RUNNER_USERS_FILE"]).parent
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.stat().st_uid != os.geteuid() or root.stat().st_mode & 0o077:
        raise ValueError("Credential storage must be private and owned by the service account")
    database = root / "controllers.sqlite3"
    key = root / "controllers.key"
    if not key.exists():
        if database.exists():
            raise ValueError("Credential encryption key is missing; restore it from backup")
        fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(Fernet.generate_key())
    if key.is_symlink() or key.stat().st_uid != os.geteuid() or key.stat().st_mode & 0o077:
        raise ValueError("Credential encryption key permissions are unsafe")
    cipher = Fernet(key.read_bytes())
    if database.is_symlink():
        raise ValueError("Credential database must not be a symbolic link")
    fd = os.open(database, os.O_WRONLY | os.O_CREAT, 0o600)
    os.close(fd)
    if database.stat().st_uid != os.geteuid() or database.stat().st_mode & 0o077:
        raise ValueError("Credential database permissions are unsafe")
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE IF NOT EXISTS controllers (id TEXT PRIMARY KEY, data TEXT NOT NULL, secret BLOB NOT NULL)")
    connection.commit()
    return connection, cipher


def _controller_public(row):
    return dict(json.loads(row[1]), profile_id=row[0], credential_saved=True)


@app.get("/api/controller-profiles")
def controller_profiles_list():
    try:
        with _profile_lock:
            connection, _ = _profile_store()
            with connection:
                rows = connection.execute("SELECT id, data FROM controllers ORDER BY id").fetchall()
            connection.close()
        return jsonify([_controller_public(row) for row in rows])
    except Exception:
        app.logger.error("Unable to access controller profile storage")
        return jsonify(error="Controller profiles unavailable. Check protected credential storage."), 503


@app.post("/api/controller-profiles")
def controller_profile_save():
    data = request.get_json(silent=True) or {}
    try:
        value = {}
        for field in ("name", "host", "username", "verify"):
            item = data.get(field, "")
            if not isinstance(item, str) or len(item) > 256:
                raise ValueError("Invalid controller field")
            value[field] = item.strip()
        if not all(value[field] for field in ("name", "host", "username")):
            raise ValueError("Controller name, host and username are required")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*(?::[0-9]{1,5})?", value["host"]):
            raise ValueError("Enter a hostname or IPv4 address with optional port, not a URL")
        if value["verify"] not in ("", "true", "false"):
            raise ValueError("Invalid TLS verification setting")
        password = data.get("password", "")
        if not isinstance(password, str) or len(password) > 4096:
            raise ValueError("Invalid controller password")
        pid = data.get("profile_id") or uuid.uuid4().hex
        if not isinstance(pid, str) or not re.fullmatch(r"[a-f0-9]{32}", pid):
            raise ValueError("Invalid controller profile ID")
        with _profile_lock:
            connection, cipher = _profile_store()
            try:
                previous = connection.execute("SELECT data, secret FROM controllers WHERE id=?", (pid,)).fetchone()
                if data.get("profile_id") and previous is None:
                    raise ValueError("Controller profile no longer exists")
                if not password and (previous is None or any(
                        json.loads(previous[0])[field] != value[field] for field in ("host", "username"))):
                    raise ValueError("Enter a password for a new controller or changed host/username")
                encrypted = cipher.encrypt(password.encode()) if password else previous[1]
                with connection:
                    connection.execute("INSERT OR REPLACE INTO controllers VALUES (?, ?, ?)",
                                       (pid, json.dumps(value), encrypted))
            finally:
                connection.close()
        return jsonify(dict(value, profile_id=pid, credential_saved=True))
    except ValueError:
        return jsonify(error="Unable to save connection. Check name, host, username and TLS setting; enter a password for a new or changed controller. Existing profile IDs must still exist. Storage and key permissions must be private."), 400
    except Exception:
        app.logger.error("Unable to save controller credentials")
        return jsonify(error="Unable to save controller. Check protected credential storage."), 503


@app.delete("/api/controller-profiles/<pid>")
def controller_profile_delete(pid):
    try:
        with _profile_lock:
            connection, _ = _profile_store()
            with connection:
                connection.execute("DELETE FROM controllers WHERE id=?", (pid,))
            connection.close()
        return jsonify(deleted=True)
    except Exception:
        app.logger.error("Unable to delete controller profile")
        return jsonify(error="Unable to delete controller profile."), 503


def _resolve_controller_reference(value):
    if not isinstance(value, dict) or not value.get("profile_id"):
        return value
    if value.get("password"):
        raise ValueError("Save changed credentials before using this connection")
    with _profile_lock:
        connection, cipher = _profile_store()
        try:
            row = connection.execute("SELECT id, data, secret FROM controllers WHERE id=?", (value["profile_id"],)).fetchone()
        finally:
            connection.close()
    if row is None:
        raise ValueError("Saved controller no longer exists. Select another controller.")
    saved = _controller_public(row)
    if any(value.get(field) is not None and value[field] != saved[field]
           for field in ("host", "username", "verify")):
        raise ValueError("Controller settings changed. Reload the saved connection before running.")
    return dict(saved, enabled=True, password=cipher.decrypt(row[2]).decode())


def resolve_controller_profiles():
    # Authorize and resolve before dispatching work to threads without request context.
    if not getattr(g, "runner_user", None) or request.endpoint not in {
            "api_run", "api_run_suite", "api_run_suites", "api_run_batch",
            "api_device_interfaces", "api_host_port_assignments"}:
        return None
    try:
        def hydrate(data):
            if not isinstance(data, dict):
                return
            if "catalyst_connection" in data:
                data["catalyst_connection"] = _resolve_controller_reference(data["catalyst_connection"])
            for run in data.get("runs", []) + data.get("suites", []):
                hydrate(run)
            for target in data.get("targets", []):
                if isinstance(target, dict):
                    target["connection"] = _resolve_controller_reference(target.get("connection") or target)
        hydrate(request.get_json(silent=True) or {})
    except Exception:
        return jsonify(error="Saved controller unavailable or changed. Reload connections, or ask an administrator to check credentials."), 400


def _accounts():
    users = json.loads(Path(app.config["RUNNER_USERS_FILE"]).read_text())
    if not isinstance(users, dict) or not users:
        raise ValueError("Invalid account configuration")
    for name, user in users.items():
        if (not isinstance(user, dict) or user.get("role") not in _roles
                or not isinstance(user.get("password_hash"), str)
                or not user["password_hash"].startswith("scrypt:")
                or not isinstance(user.get("enabled", True), bool)):
            raise ValueError("Invalid account configuration")
    return users


@app.before_request
def require_access():
    if app.testing and app.config.get("RUNNER_TEST_AUTH_BYPASS", False):
        return None
    if request.endpoint == "static":
        return None
    try:
        if not app.secret_key:
            raise ValueError("Missing secret")
        users = _accounts()
    except (OSError, ValueError, TypeError):
        if request.path.startswith("/api/"):
            return jsonify(error="Login is not configured. Ask the administrator to initialize accounts."), 503
        return render_template("login.html", setup=True), 503
    if request.endpoint == "login" and request.method == "GET" and session.get("sid"):
        with _auth_lock:
            known_session = _auth_sessions.get(session["sid"])
        if not known_session or known_session[2] < time.time():
            session.clear()
    session.setdefault("csrf", secrets.token_urlsafe(32))
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        token = request.headers.get("X-CSRF-Token", "") or request.form.get("csrf", "")
        if not secrets.compare_digest(token, session["csrf"]):
            return jsonify(error="Invalid or expired security token. Reload the page."), 403
    if request.endpoint == "login":
        return None
    user = users.get(session.get("username"), {})
    version = hashlib.sha256(user.get("password_hash", "").encode()).hexdigest()
    with _auth_lock:
        valid = _auth_sessions.get(session.get("sid"))
    if not valid or valid[:2] != (session.get("username"), version) or valid[2] < time.time() or not user.get("enabled", True):
        if session.get("username") or session.get("sid"):
            session.clear()
        if request.path.startswith("/api/"):
            return jsonify(error="Sign in required."), 401
        return redirect(url_for("login"))
    g.runner_user = {"username": session["username"], "role": user["role"]}
    if request.endpoint == "logout":
        return None
    required = (0 if request.endpoint in _read_endpoints else
                1 if request.endpoint in _operator_endpoints else
                2 if request.endpoint in _admin_endpoints else 99)
    if _roles[user["role"]] < required:
        return jsonify(error="Your account does not have permission for this action."), 403


app.before_request(resolve_controller_profiles)


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    if request.endpoint != "static":
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        key = request.remote_addr or "unknown"
        now = time.monotonic()
        with _auth_lock:
            attempts = [stamp for stamp in _auth_attempts.get(key, []) if now - stamp < 300]
            if len(attempts) >= 10:
                return render_template("login.html", error="Too many attempts. Try again in five minutes."), 429
            if len(_auth_attempts) > 10000:
                _auth_attempts.clear()
            _auth_attempts[key] = attempts + [now]
        username = request.form.get("username", "").strip()
        user = _accounts().get(username, {})
        # Use the same expensive hash operation for unknown accounts.
        password_hash = user.get("password_hash") or _dummy_password_hash
        if check_password_hash(password_hash, request.form.get("password", "")) and user.get("enabled", True):
            session.clear()
            session.permanent = True
            session.update(username=username, sid=secrets.token_urlsafe(32), csrf=secrets.token_urlsafe(32))
            with _auth_lock:
                expired = [sid for sid, value in _auth_sessions.items() if value[2] < time.time()]
                for sid in expired:
                    _auth_sessions.pop(sid, None)
                _auth_sessions[session["sid"]] = (username, hashlib.sha256(password_hash.encode()).hexdigest(), time.time() + 28800)
                _auth_attempts.pop(key, None)
            return redirect(url_for("index"))
        error = "Invalid username or password."
    return render_template("login.html", error=error), (401 if error else 200)


@app.post("/logout")
def logout():
    with _auth_lock:
        _auth_sessions.pop(session.get("sid"), None)
    session.clear()
    return redirect(url_for("login"))

# Project root is two levels up: tools/ansible_runner/app.py -> repo root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / "workflows"
INVENTORY_DIR = PROJECT_ROOT / "inventory"
GIT_REPOS_DIR = PROJECT_ROOT / ".runner_repos"
HOME_DIR = Path.home().resolve()
YAML_SUFFIXES = {".yml", ".yaml"}
VERBOSITY_FLAGS = {"", "-v", "-vv", "-vvv", "-vvvv"}
DEFAULT_VENV = PROJECT_ROOT / ".venv312"
DEPENDENCY_REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
GITHUB_REPO_URL_RE = re.compile(r"^/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$")
GIT_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")
SAFE_RELATIVE_PATH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,500}$")
BROWSE_ROOTS = {
    "repo": ("Repository", PROJECT_ROOT.resolve()),
    "home": ("Home", HOME_DIR),
}

# Live process handles stay in memory; history and logs are durable.
_jobs: dict[str, "Job"] = {}
_jobs_lock = threading.Lock()
_cancelled_suites: set[str] = set()
_active_suites: set[str] = set()
_history_lock = threading.RLock()
_history_ready = None
app.config["RUNNER_HISTORY_DIR"] = os.environ.get(
    "RUNNER_HISTORY_DIR", str(Path.home() / ".local/share/catalystcenter-runner"))


def _history_dir():
    if app.testing and not app.config.get("RUNNER_TEST_HISTORY", False):
        return None
    return Path(app.config["RUNNER_HISTORY_DIR"]).expanduser().resolve()


def _history_connection(root):
    connection = sqlite3.connect(root / "history.sqlite3", timeout=30)
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("PRAGMA secure_delete=ON")
    return connection


_SECRET_KEY = re.compile(r"password|passwd|secret|token|community|private[_-]?key", re.I)
_SECRET_ASSIGNMENT = re.compile(
    r'''(["']?[\w.-]*(?:password|passwd|secret|token|community|private[_-]?key)[\w.-]*["']?\s*[:=]\s*)(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\r\n]*)''', re.I)


def _credential_values(value):
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if _SECRET_KEY.search(str(key)) and isinstance(item, str) and item:
                found.add(item)
            found.update(_credential_values(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_credential_values(item))
    return found


def _history_metadata(metadata):
    # Never store execution credentials or arbitrary extra arguments in SQLite.
    allowed = {"kind", "batch_id", "suite_launch_id", "suite_name", "suite_run_index",
               "suite_run_total", "suite_failure_policy", "suite_launch_mode", "suite_plan",
               "suite_finished", "label", "workflow", "playbook", "inventory", "vars_file",
               "inventory_embedded", "submitted_by", "vars_source", "inventory_source",
               "catalyst_connection_host", "catalyst_connection_username",
               "catalyst_connection_verify", "catalyst_connection_profile_id",
               "catalyst_connection_enabled", "managed_venv", "venv_path", "verbosity",
               "rerun_of", "rerun_job_id", "rerun_requires_options"}
    result = {key: value for key, value in metadata.items() if key in allowed}
    result["rerun_requires_options"] = bool(metadata.get("extra_args") or metadata.get("rerun_requires_options"))
    for field in ("vars_source", "inventory_source"):
        if field in result:
            source = result[field] if isinstance(result[field], dict) else {}
            result[field] = {key: source[key] for key in ("kind", "id") if key in source}
    if isinstance(result.get("suite_plan"), list):
        result["suite_plan"] = [{key: value for key, value in item.items()
                                 if key in {"index", "workflow", "playbook", "vars_file", "inventory", "inventory_embedded"}}
                                for item in result["suite_plan"] if isinstance(item, dict)]
    return result


@app.before_request
def load_history():
    global _history_ready
    root = _history_dir()
    if root is None or _history_ready == root:
        return None
    try:
        with _history_lock:
            if _history_ready == root:
                return None
            if root in {Path(root.anchor), Path.home().resolve(), PROJECT_ROOT.resolve()}:
                raise ValueError("History requires a dedicated directory")
            root.mkdir(parents=True, exist_ok=True, mode=0o700)
            root.chmod(0o700)
            (root / "logs").mkdir(exist_ok=True, mode=0o700)
            (root / "logs").chmod(0o700)
            database = root / "history.sqlite3"
            fd = os.open(database, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
            database.chmod(0o600)
            with _history_connection(root) as connection:
                connection.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, data TEXT NOT NULL)")
                connection.execute("CREATE TABLE IF NOT EXISTS saved_suites (id TEXT PRIMARY KEY, owner TEXT NOT NULL, revision INTEGER NOT NULL, position INTEGER NOT NULL, data TEXT NOT NULL)")
                connection.execute("CREATE TABLE IF NOT EXISTS history_deletions (id TEXT PRIMARY KEY, jobs TEXT NOT NULL)")
            with _history_connection(root) as connection:
                pending = connection.execute("SELECT id,jobs FROM history_deletions").fetchall()
            for request_id, ids in pending:
                _finish_history_deletion(root, request_id, json.loads(ids))
            with _history_connection(root) as connection:
                for jid, raw in connection.execute("SELECT id, data FROM jobs").fetchall():
                    if not re.fullmatch(r"[a-f0-9]{8}", jid):
                        raise ValueError("Invalid stored job identifier")
                    data = json.loads(raw)
                    metadata = data.get("metadata") or {}
                    unfinished = data["status"] in {"queued", "running", "waiting"}
                    suite_unfinished = metadata.get("suite_launch_id") and not metadata.get("suite_finished")
                    if unfinished or suite_unfinished:
                        if unfinished:
                            data.update(status="interrupted", t1=time.time())
                        metadata["suite_finished"] = True
                        connection.execute("UPDATE jobs SET data=? WHERE id=?", (json.dumps(data), jid))
                    job = Job(jid, [], data.get("cwd", ""), data.get("label", ""), metadata=metadata)
                    job.status, job.rc = data["status"], data.get("rc")
                    job.t0, job.t1 = data.get("t0"), data.get("t1")
                    if job.status == "interrupted":
                        job.recovered_pid = data.get("process_pid")
                    log = root / "logs" / (jid + ".jsonl")
                    if log.exists():
                        needs_redaction = False
                        with log.open() as stream:
                            for line in stream:
                                try:
                                    original = json.loads(line)
                                    sanitized = job.redact_output(original)
                                    needs_redaction |= sanitized != original
                                    job.lines.append(sanitized)
                                except ValueError:
                                    job.lines.append("*** Incomplete log record after interruption.\n")
                                    needs_redaction = True
                        if needs_redaction:
                            _rewrite_redacted_log(log, job.lines)
                    if unfinished:
                        job.lines.append("*** Runner restarted; monitoring was interrupted. The playbook may still be running. Verify before retrying; it was not automatically resumed.\n")
                    _jobs[jid] = job
                # Unreferenced log files may remain after a crash during deletion.
                for log in (root / "logs").glob("*.jsonl"):
                    if log.stem not in _jobs:
                        log.unlink()
            _history_ready = root
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error):
        app.logger.exception("Unable to initialize persistent history")
        return jsonify(error="Persistent history is unavailable. Check storage permissions and server logs."), 503


def _persist_job(job):
    root = _history_dir()
    if root is None or job._deleted:
        return
    data = job.info()
    data["cmd"] = ""  # Commands may embed secrets; history is not a replay queue.
    data["metadata"] = _history_metadata(job.metadata)
    pid = job.proc.pid if job.proc is not None else job.recovered_pid
    data["process_pid"] = pid if isinstance(pid, int) else None
    with _history_lock:
        if job._deleted:
            return
        with _history_connection(root) as connection:
            connection.execute("INSERT INTO jobs(id,data) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                               (job.id, json.dumps(data)))


def _rewrite_redacted_log(path, lines):
    descriptor, temporary = tempfile.mkstemp(prefix=".redact-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            for line in lines:
                stream.write(json.dumps(line) + "\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


# ---------------------------------------------------------------------------
# Job model
# ---------------------------------------------------------------------------
class Job:
    """Represents a single ansible-playbook execution."""

    def __init__(
        self,
        jid: str,
        argv: list[str],
        cwd: str,
        label: str = "",
        env_overrides: dict[str, str] | None = None,
        metadata: dict | None = None,
    ):
        self.id = jid
        self.argv = argv
        self.cmd = shlex.join(argv)
        self.cwd = cwd
        self.label = label
        self.env_overrides = env_overrides or {}
        self.metadata = metadata or {}
        self.embedded_inventory: dict | None = None
        self.status = "queued"
        self.lines: list[str] = []
        self.proc: subprocess.Popen | None = None
        self.t0: float | None = None
        self.t1: float | None = None
        self.rc: int | None = None
        self._lock = threading.Lock()
        self._deleted = False
        self.recovered_pid = None
        self.secret_values = _credential_values(self.env_overrides) | _credential_values(dict(os.environ))
        self._private_key_output = False

    def public_command(self):
        # Extra arguments, interpreter overrides and inventory vars can contain secrets.
        executable = Path(self.argv[0]).name if self.argv else "ansible-playbook"
        return shlex.join([executable, str(self.metadata.get("playbook") or "<playbook>")])

    def capture_input_secrets(self, paths=()):
        import yaml
        self.secret_values.update(_credential_values(dict(os.environ)))
        for path in paths:
            if path:
                try:
                    self.secret_values.update(_credential_values(yaml.safe_load(Path(path).read_text())))
                except (OSError, ValueError, yaml.YAMLError):
                    pass
        for argument in self.argv:
            try:
                self.secret_values.update(_credential_values(yaml.safe_load(argument)))
                for part in shlex.split(argument):
                    key, separator, value = part.partition("=")
                    if separator and value and _SECRET_KEY.search(key):
                        self.secret_values.add(value)
            except (ValueError, yaml.YAMLError):
                pass

    def redact_output(self, line):
        if not isinstance(line, str):
            return "[REDACTED invalid log record]\n"
        if re.search(r"-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----", line):
            self._private_key_output = True
        if self._private_key_output:
            if re.search(r"-----END (?:[A-Z ]*PRIVATE KEY)-----", line):
                self._private_key_output = False
            return "[REDACTED private key]\n"
        for secret in sorted(self.secret_values, key=len, reverse=True):
            line = line.replace(secret, "[REDACTED]")
        line = _SECRET_ASSIGNMENT.sub(lambda match: match.group(1) + '"[REDACTED]"', line)
        line = re.sub(r"(?i)(Authorization\s*[:=]\s*)([^\r\n]+)", r"\1[REDACTED]", line)
        return re.sub(r"([A-Za-z][A-Za-z0-9+.-]*://)[^/\s@]+@", r"\1[REDACTED]@", line)

    def put(self, line: str):
        with self._lock:
            if self._deleted:
                return
            line = self.redact_output(line)
            root = _history_dir()
            if root is not None:
                with _history_lock:
                    with open(root / "logs" / (self.id + ".jsonl"), "a",
                              opener=lambda p, f: os.open(p, f, 0o600)) as stream:
                        stream.write(json.dumps(line) + "\n")
            self.lines.append(line)

    def info(self):
        return dict(
            id=self.id,
            cmd=self.public_command(),
            label=self.label,
            cwd=self.cwd,
            status=self.status,
            rc=self.rc,
            t0=self.t0,
            t1=self.t1,
            n=len(self.lines),
            metadata={key: value for key, value in self.metadata.items() if key != "extra_args"},
        )

    def details(self):
        with self._lock:
            lines = list(self.lines)
        data = self.info()
        data["lines"] = lines
        return data


def _exec(job: Job):
    """Execute ansible-playbook in a background thread."""
    with job._lock:
        if job.status == "cancelled" or job.metadata.get("suite_launch_id") in _cancelled_suites:
            job.status = "cancelled"
            job.t1 = time.time()
            _persist_job(job)
            return
    env = os.environ.copy()
    env["ANSIBLE_FORCE_COLOR"] = "true"
    env["PYTHONUNBUFFERED"] = "1"
    env.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
    env.setdefault("ANSIBLE_FORKS", "1")
    env.update(job.env_overrides)
    inventory_workspace = None
    try:
        if job.embedded_inventory is not None:
            import yaml

            inventory_workspace = tempfile.TemporaryDirectory(prefix="runner-inventory-")
            inventory_file = Path(inventory_workspace.name) / "hosts.yml"
            with open(inventory_file, "x", opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
                yaml.safe_dump(job.embedded_inventory, stream)
            job.argv[job.argv.index("-i") + 1] = str(inventory_file)
            job.cmd = shlex.join(job.argv)
        # Serialize cancellation with process creation, including the queued state.
        with job._lock:
            if job.status == "cancelled" or job.metadata.get("suite_launch_id") in _cancelled_suites:
                job.status = "cancelled"
                return
            job.proc = subprocess.Popen(
                job.argv,
                cwd=job.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                start_new_session=True,
                env=env,
            )
            job.status = "running"
            job.t0 = time.time()
            _persist_job(job)
        if job.proc.stdout is not None:
            for line in iter(job.proc.stdout.readline, ""):
                job.put(line)
        job.proc.wait()
        job.rc = job.proc.returncode
        with job._lock:
            if job.status != "cancelled":
                job.status = "completed" if job.rc == 0 else "failed"
    except Exception:
        app.logger.exception("Job execution failed")
        job.put("\n*** Unable to execute playbook. Check the runner server log.\n")
        with job._lock:
            if job.status != "cancelled":
                job.status = "failed"
    finally:
        if job.proc is not None and job.proc.stdout is not None:
            job.proc.stdout.close()
        if inventory_workspace is not None:
            inventory_workspace.cleanup()
        job.t1 = time.time()
        _persist_job(job)


def _exec_with_semaphore(job: Job, semaphore: threading.Semaphore):
    with semaphore:
        if job.status == "cancelled":
            job.t1 = time.time()
            _persist_job(job)
            return
        _exec(job)


def _suite_failed_start_job(data: dict, message: str, *, kind: str = "automation-suite") -> Job:
    jid = data.get("_reserved_job_id") or uuid.uuid4().hex[:8]
    label = data.get("label") or f"Play {data.get('suite_run_index') or ''}".strip() or "Automation suite play"
    metadata = {
        "kind": kind,
        "submitted_by": data.get("_submitted_by", ""),
        "batch_id": "",
        "suite_launch_id": data.get("suite_launch_id") or "",
        "suite_name": data.get("suite_name") or "",
        "suite_run_index": data.get("suite_run_index") or "",
        "suite_run_total": data.get("suite_run_total") or "",
        "suite_failure_policy": data.get("suite_failure_policy") or "",
        "suite_launch_mode": data.get("suite_launch_mode") or "",
        "suite_plan": data.get("suite_plan") if isinstance(data.get("suite_plan"), list) else [],
        "label": label,
        "workflow": data.get("workflow") or "",
        "playbook": data.get("playbook") or "",
        "inventory": data.get("inventory") or "",
        "vars_file": data.get("vars_file") or "",
        "vars_source": data.get("vars_source") or {},
        "inventory_source": data.get("inventory_source") or {},
        "extra_args": data.get("extra_args", ""),
        "managed_venv": data.get("managed_venv", ""),
        "venv_path": data.get("venv_path") or "",
        "catalyst_connection_enabled": bool((data.get("catalyst_connection") or {}).get("enabled")),
        "catalyst_connection_host": str((data.get("catalyst_connection") or {}).get("host") or ""),
        "catalyst_connection_username": str((data.get("catalyst_connection") or {}).get("username") or ""),
        "catalyst_connection_verify": str((data.get("catalyst_connection") or {}).get("verify") or ""),
        "catalyst_connection_password_set": bool((data.get("catalyst_connection") or {}).get("password")),
    }
    job = Job(jid, ["suite-start-failed"], str(PROJECT_ROOT), label, {}, metadata)
    job.status = "failed"
    job.rc = 1
    job.t0 = time.time()
    job.t1 = job.t0
    job.put(f"*** Failed to start suite play: {message}\n")
    return job


def _exec_suite_sequence(runs: list[dict], failure_policy: str):
    try:
        _exec_suite_sequence_inner(runs, failure_policy)
    finally:
        suite_ids = {run.get("suite_launch_id") for run in runs if run.get("suite_launch_id")}
        with _jobs_lock:
            for job in _jobs.values():
                if job.metadata.get("suite_launch_id") in suite_ids:
                    job.metadata["suite_finished"] = True
                    if job.status == "queued":
                        job.status = "cancelled" if job.metadata.get("suite_launch_id") in _cancelled_suites else "not-run"
                        job.t1 = time.time()
                    _persist_job(job)
            _active_suites.difference_update(suite_ids)


def _exec_suite_sequence_inner(runs: list[dict], failure_policy: str):
    continue_on_failure = failure_policy == "continue"
    for data in runs:
        suite_id = data.get("suite_launch_id") or ""
        if suite_id in _cancelled_suites:
            break
        reserved = _jobs.get(data.get("_reserved_job_id"))
        if reserved is not None and reserved.status == "cancelled":
            if not continue_on_failure:
                break
            continue
        job, result = _build_run_job(data, kind=data.get("kind") or "automation-suite")
        if job is None:
            failed_job = _suite_failed_start_job(data, str(result))
            _install_suite_job(failed_job)
            if not continue_on_failure:
                break
            continue
        job = _install_suite_job(job)
        if job is None:
            if not continue_on_failure:
                break
            continue
        _exec(job)
        if suite_id in _cancelled_suites:
            break
        if job.status != "completed" and not continue_on_failure:
            break


def _install_suite_job(prepared):
    # Keep the registered object stable so in-flight cancellation keeps its lock/state.
    with _jobs_lock:
        reserved = _jobs.get(prepared.id)
        if reserved is not None:
            with reserved._lock:
                if reserved.status == "cancelled" or reserved._deleted:
                    return None
                for name in ("argv", "cmd", "cwd", "label", "env_overrides", "metadata", "embedded_inventory",
                             "status", "rc", "t0", "t1", "lines", "secret_values"):
                    setattr(reserved, name, getattr(prepared, name))
                prepared = reserved
        _jobs[prepared.id] = prepared
        _persist_job(prepared)
        return prepared


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _is_within(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def _display_path(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _display_source_path(path: Path | None, source_root: Path | None = None) -> str:
    if path is None:
        return ""
    if source_root is not None:
        try:
            return str(path.relative_to(source_root))
        except ValueError:
            pass
    return _display_path(path)


def _resolve_local_path(
    raw_path: str | None,
    *,
    roots: tuple[Path, ...],
    must_exist: bool = True,
) -> Path | None:
    """Resolve relative or absolute paths while keeping them inside allowed roots."""
    if not raw_path:
        return None

    candidate = _confined_path(raw_path, roots, PROJECT_ROOT)
    if candidate is None:
        return None
    if must_exist and not candidate.exists():
        return None
    return candidate


def _confined_path(raw_path: str, roots: tuple[Path, ...], relative_root: Path) -> Path | None:
    """Reject traversal before filesystem access, then check resolved symlinks."""
    if not isinstance(raw_path, str) or "\x00" in raw_path:
        return None
    expanded = os.path.expanduser(raw_path)
    absolute = os.path.abspath(os.path.join(str(relative_root), expanded))
    for root in roots:
        relative = os.path.relpath(absolute, root)
        joined = safe_join(str(root), relative)
        if joined is None:
            continue
        candidate = Path(joined).resolve()
        if candidate.is_relative_to(root.resolve()):
            return candidate
    return None


def _resolve_repo_path(raw_path: str | None, *, must_exist: bool = True) -> Path | None:
    return _resolve_local_path(raw_path, roots=(PROJECT_ROOT.resolve(),), must_exist=must_exist)


def _resolve_user_file(raw_path: str | None, *, must_exist: bool = True) -> Path | None:
    return _resolve_local_path(
        raw_path,
        roots=(PROJECT_ROOT.resolve(), HOME_DIR),
        must_exist=must_exist,
    )


def _git_source_id() -> str:
    return f"repo_{uuid.uuid4().hex[:12]}"


_repo_fetch_locks = {}


def _repo_catalog_database():
    connection = _suite_database()
    connection.execute("CREATE TABLE IF NOT EXISTS git_repositories (id TEXT PRIMARY KEY, repo_url TEXT NOT NULL, ref TEXT NOT NULL, data TEXT NOT NULL, UNIQUE(repo_url, ref))")
    connection.commit()
    return connection


def _registered_repo(repo_url, ref):
    with _history_lock:
        connection = _repo_catalog_database()
        try:
            row = connection.execute("SELECT data FROM git_repositories WHERE repo_url=? AND ref=?", (repo_url, ref)).fetchone()
        finally:
            connection.close()
    return json.loads(row[0]) if row else None


@app.get("/api/git/repositories")
def git_repositories_list():
    try:
        with _history_lock:
            connection = _repo_catalog_database()
            try:
                records = [json.loads(row[0]) for row in connection.execute("SELECT data FROM git_repositories ORDER BY repo_url, ref")]
            finally:
                connection.close()
        for record in records:
            root = _resolve_git_source(record["source"])
            record["available"] = root is not None
            if root is not None:
                record["vars"] = _discover_repo_vars(root)
                record["inventories"] = _discover_inventories(root)
        return jsonify(records)
    except (OSError, ValueError, sqlite3.Error):
        app.logger.error("Unable to load shared repository catalog")
        return _json_error("Shared repository catalog unavailable. Check server storage.", 503)


@app.delete("/api/git/repositories/<source_id>")
def git_repository_remove(source_id):
    try:
        with _history_lock:
            connection = _repo_catalog_database()
            try:
                row = connection.execute("SELECT repo_url, ref FROM git_repositories WHERE id=?", (source_id,)).fetchone()
                if row is None:
                    return _json_error("Repository not found. Refresh the catalog.", 404)
                lock = _repo_fetch_locks.setdefault(tuple(row), threading.Lock())
                if not lock.acquire(blocking=False):
                    return _json_error("Repository fetch is in progress. Retry after it finishes.", 409)
                try:
                    with connection:
                        connection.execute("DELETE FROM git_repositories WHERE id=?", (source_id,))
                finally:
                    lock.release()
            finally:
                connection.close()
        # Keep snapshots: existing suites/jobs may still reference these inputs.
        return jsonify(removed=source_id)
    except (OSError, sqlite3.Error):
        app.logger.error("Unable to remove shared repository record")
        return _json_error("Unable to remove repository. Check server storage.", 503)


def _normalize_git_input(repo_url: str, ref: str) -> tuple[str, str]:
    """Accept common GitHub browser URLs and convert them to clone URLs."""
    cleaned_url = repo_url.strip()
    cleaned_ref = ref.strip() or "main"
    match = re.match(r"^(https://github\.com/[^/]+/[^/]+?)(?:\.git)?/tree/([^/?#]+)", cleaned_url)
    if match:
        cleaned_url = match.group(1) + ".git"
        cleaned_ref = match.group(2)
    elif cleaned_url.startswith("https://github.com/") and not cleaned_url.endswith(".git"):
        cleaned_url = cleaned_url.rstrip("/") + ".git"
    return cleaned_url, cleaned_ref


def _validate_git_input(repo_url: str, ref: str) -> str | None:
    parsed = urlparse(repo_url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        return "Only https://github.com repositories are supported"
    if parsed.params or parsed.query or parsed.fragment or not GITHUB_REPO_URL_RE.fullmatch(parsed.path):
        return "Git repository URL must be in owner/repo format"
    if not GIT_REF_RE.fullmatch(ref) or ".." in ref or "@{" in ref or "\\" in ref or ref.endswith(("/", ".")):
        return "Git ref must be a branch, tag, or commit-like value"
    return None


def _git_repo_cache_target() -> tuple[str, Path]:
    source_id = _git_source_id()
    target = (GIT_REPOS_DIR / source_id).resolve()
    return source_id, target


def _resolve_existing_git_repo_cache_dir(source_id: str) -> Path | None:
    if not re.fullmatch(r"repo_[0-9a-f]{12}", source_id):
        return None
    cache_root = GIT_REPOS_DIR.resolve()
    if not cache_root.exists():
        return None
    for child in cache_root.iterdir():
        if child.name != source_id:
            continue
        source_root = child.resolve()
        if _is_within(source_root, cache_root) and source_root.exists():
            return source_root
    return None


def _resolve_git_source(source: dict | None) -> Path | None:
    if not source or source.get("kind") != "git":
        return PROJECT_ROOT.resolve()
    source_id = str(source.get("id") or "")
    return _resolve_existing_git_repo_cache_dir(source_id)


def _safe_relative_parts(raw_path: str) -> tuple[str, ...] | None:
    if not SAFE_RELATIVE_PATH_RE.fullmatch(raw_path) or "\\" in raw_path:
        return None
    parts = tuple(part for part in raw_path.split("/") if part)
    if not parts or any(part in {".", ".."} or part.startswith(".") for part in parts):
        return None
    return parts


def _find_existing_relative_yaml(root: Path, raw_path: str) -> Path | None:
    parts = _safe_relative_parts(raw_path)
    if not parts:
        return None
    expected = "/".join(parts)
    ignored_parts = {".git", ".venv", ".venv312", "venv", "__pycache__", ".runner_repos"}
    for candidate in root.rglob("*"):
        if not candidate.is_file() or candidate.suffix.lower() not in YAML_SUFFIXES:
            continue
        rel_path = candidate.relative_to(root)
        if ignored_parts.intersection(rel_path.parts):
            continue
        if rel_path.as_posix() == expected:
            return candidate.resolve()
    return None


def _resolve_source_file(
    raw_path: str | None,
    source_root: Path,
    *,
    must_exist: bool = True,
    allow_user_file: bool = True,
    allow_project_fallback: bool = True,
) -> Path | None:
    if not raw_path:
        return None

    raw_path = raw_path.strip()
    if os.path.isabs(raw_path):
        if source_root != PROJECT_ROOT.resolve():
            candidate = _resolve_local_path(raw_path, roots=(source_root,), must_exist=must_exist)
            return candidate if candidate and candidate.suffix.lower() in YAML_SUFFIXES else None
        if allow_user_file:
            candidate = _resolve_user_file(raw_path, must_exist=must_exist)
            return candidate if candidate and candidate.suffix.lower() in YAML_SUFFIXES else None
        return None

    source_candidate = _find_existing_relative_yaml(source_root, raw_path)
    if source_candidate and _is_within(source_candidate, source_root):
        return source_candidate
    if not must_exist:
        return None

    return None


def _discover_inventories(root: Path) -> list[str]:
    inventory_dir = root / "inventory"
    out = []
    if not inventory_dir.is_dir():
        return out
    for current_root, _dirs, files in os.walk(inventory_dir):
        for filename in files:
            if filename.endswith((".yml", ".yaml")):
                out.append(os.path.relpath(os.path.join(current_root, filename), root))
    return sorted(out)


def _looks_like_playbook(path: Path) -> bool:
    try:
        text = path.read_text(errors="ignore")[:200000]
    except OSError:
        return False
    return bool(re.search(r"(?m)^\s*-\s+(?:name:\s*.*\n\s*)?hosts\s*:", text) or re.search(r"(?m)^\s*hosts\s*:", text))


def _discover_repo_vars(root: Path) -> list[str]:
    ignored_parts = {".git", ".venv", ".venv312", "venv", "__pycache__", ".runner_repos"}
    out = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in YAML_SUFFIXES:
            continue
        rel_path = path.relative_to(root)
        parts = rel_path.parts
        if ignored_parts.intersection(parts):
            continue
        lower_parts = [part.lower() for part in parts]
        lower_name = path.name.lower()
        if lower_name.startswith("hosts.") or (lower_parts and lower_parts[0] == "inventory"):
            continue
        if "schema" in lower_parts or "playbook" in lower_parts:
            continue
        if not (
            "vars" in lower_parts
            or "var" in lower_name
            or "input" in lower_name
            or (len(lower_parts) >= 3 and lower_parts[0] == "data" and lower_name == "data.yml")
        ):
            continue
        if _looks_like_playbook(path):
            continue
        out.append(str(rel_path))
    return sorted(dict.fromkeys(out))


def _discover_standalone_playbooks(root: Path) -> list[dict]:
    ignored_parts = {".git", ".venv", ".venv312", "venv", "__pycache__", ".runner_repos"}
    repo_vars = _discover_repo_vars(root)
    records = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in YAML_SUFFIXES:
            continue
        if ignored_parts.intersection(path.relative_to(root).parts):
            continue
        if "/vars/" in str(path.relative_to(root)) or "/schema/" in str(path.relative_to(root)):
            continue
        if not _looks_like_playbook(path):
            continue
        rel = str(path.relative_to(root))
        records.append(
            {
                "name": path.stem,
                "playbooks": [rel],
                "vars": repo_vars,
                "schemas": [],
                "has_readme": False,
                "standalone": True,
            }
        )
    return records


def _discover_workflows(root: Path) -> list[dict]:
    workflows_dir = root / "workflows"
    out = []
    if workflows_dir.is_dir():
        for directory in sorted(workflows_dir.iterdir()):
            if not directory.is_dir() or directory.name.startswith("."):
                continue

            record = dict(name=directory.name, playbooks=[], vars=[], schemas=[], has_readme=False)
            for subdir, key in [("playbook", "playbooks"), ("vars", "vars"), ("schema", "schemas")]:
                path = directory / subdir
                if path.is_dir():
                    record[key] = sorted(
                        file.name
                        for file in path.iterdir()
                        if file.is_file() and file.suffix.lower() in YAML_SUFFIXES
                    )
            record["has_readme"] = (directory / "README.md").is_file()
            if record["playbooks"]:
                out.append(record)
    return out or _discover_standalone_playbooks(root)


def _git_lock_error(output: str) -> bool:
    return "File exists" in output and ".lock" in output


def _run_git_clone_branch(repo_url: str, ref: str, target: Path) -> subprocess.CompletedProcess:
    # codeql[py/command-line-injection] repo_url/ref/target are validated before this fixed-argv git call.
    return subprocess.run(
        ["git", "clone", "--filter=blob:none", "--depth", "1", "--branch", ref, repo_url, str(target)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=600,
    )


def _run_git_clone_default(repo_url: str, target: Path) -> subprocess.CompletedProcess:
    # codeql[py/command-line-injection] repo_url/target are validated before this fixed-argv git call.
    return subprocess.run(
        ["git", "clone", "--filter=blob:none", "--depth", "1", repo_url, str(target)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=600,
    )


def _run_git_checkout(ref: str, cwd: Path) -> subprocess.CompletedProcess:
    # codeql[py/command-line-injection] ref/cwd are validated before this fixed-argv git call.
    return subprocess.run(
        ["git", "checkout", ref],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=600,
    )


def _run_git_fetch_ref(ref: str, cwd: Path) -> subprocess.CompletedProcess:
    # codeql[py/command-line-injection] ref/cwd are validated before this fixed-argv git call.
    return subprocess.run(
        ["git", "fetch", "origin", ref, "--depth", "1"],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=600,
    )


def _run_git_fetch_all(cwd: Path) -> subprocess.CompletedProcess:
    # codeql[py/command-line-injection] cwd is resolved inside the managed repo cache before this fixed-argv git call.
    return subprocess.run(
        ["git", "fetch", "--all", "--tags", "--prune"],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=600,
    )


def _run_git_pull(cwd: Path) -> subprocess.CompletedProcess:
    # codeql[py/command-line-injection] cwd is resolved inside the managed repo cache before this fixed-argv git call.
    return subprocess.run(
        ["git", "pull", "--ff-only"],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=600,
    )


def _run_git_head(cwd: Path) -> subprocess.CompletedProcess:
    # codeql[py/command-line-injection] cwd is resolved inside the managed repo cache before this fixed-argv git call.
    return subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=600,
    )


def _clone_git_repo(repo_url: str, ref: str, target: Path) -> subprocess.CompletedProcess:
    if target.exists():
        shutil.rmtree(target)
    clone = _run_git_clone_branch(repo_url, ref, target)
    if clone.returncode == 0:
        return clone

    if target.exists():
        shutil.rmtree(target)
    clone = _run_git_clone_default(repo_url, target)
    if clone.returncode != 0:
        return clone

    return _run_git_checkout(ref, target)


def _browse_root(name: str | None) -> tuple[str, Path] | None:
    return BROWSE_ROOTS.get((name or "repo").lower())


def _resolve_browse_target(root: Path, raw_path: str | None) -> tuple[Path | None, Path | None]:
    """Resolve a browse request into a directory target and an optional selected file."""
    if not raw_path:
        return root, None

    candidate = _confined_path(raw_path, (root,), root)
    if candidate is None:
        return None, None

    selected_file = candidate if candidate.is_file() else None
    target_dir = selected_file.parent if selected_file else candidate
    if not target_dir.exists() or not target_dir.is_dir():
        return None, None
    return target_dir, selected_file


def _breadcrumbs(root_label: str, root: Path, current: Path) -> list[dict[str, str]]:
    crumbs = [{"name": root_label, "path": str(root)}]
    if current == root:
        return crumbs

    cursor = root
    for part in current.relative_to(root).parts:
        cursor = cursor / part
        crumbs.append({"name": part, "path": str(cursor)})
    return crumbs


def _yaml_files(path: Path) -> list[Path]:
    return sorted(
        (
            entry
            for entry in path.iterdir()
            if entry.is_file() and entry.suffix.lower() in YAML_SUFFIXES and not entry.name.startswith(".")
        ),
        key=lambda item: item.name.lower(),
    )


def _directories(path: Path) -> list[Path]:
    return sorted(
        (
            entry
            for entry in path.iterdir()
            if entry.is_dir() and not entry.name.startswith(".")
        ),
        key=lambda item: item.name.lower(),
    )


def _json_error(message: str, status: int = 400):
    return jsonify(error=message), status


def _catc_base_url(connection: dict) -> str:
    requested = str(connection.get("host") or os.environ.get("HOSTIP", "")).strip()
    configured = os.environ.get("RUNNER_CATC_ALLOWED_HOSTS", "").split(",")
    configured.append(os.environ.get("HOSTIP", ""))
    # Only administrators can add profiles; stored hosts are approved destinations.
    if (Path(app.config["RUNNER_USERS_FILE"]).parent / "controllers.sqlite3").exists():
        with _profile_lock:
            database, _ = _profile_store()
            try:
                configured.extend(json.loads(row[0])["host"] for row in database.execute("SELECT data FROM controllers"))
            finally:
                database.close()
    for host in configured:
        host = host.strip()
        if not host or host.lower() != requested.lower():
            continue
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*(?::[0-9]{1,5})?", host):
            raise ValueError("Invalid server-configured Catalyst Center host")
        return "https://" + host
    raise ValueError("Catalyst Center host is not approved by the server administrator")


class _NoCatcRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.URLError("Catalyst Center redirects are disabled")


def _catc_open(request):
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        _NoCatcRedirect(),
    )
    return opener.open(request, timeout=30)


def _catc_token(catalyst_connection: dict | None = None) -> str:
    """Return a Catalyst Center auth token without logging credentials."""
    connection = catalyst_connection or {}
    host = str(connection.get("host") or os.environ.get("HOSTIP", "")).strip()
    username = str(connection.get("username") or os.environ.get("CATALYST_CENTER_USERNAME", "")).strip()
    password = str(connection.get("password") or os.environ.get("CATALYST_CENTER_PASSWORD", ""))
    if not host or not username or not password:
        raise RuntimeError("Catalyst Center credentials are not configured in the runner")

    request = urllib.request.Request(_catc_base_url(connection) + "/dna/system/api/v1/auth/token", method="POST")
    credentials = f"{username}:{password}".encode("utf-8")
    import base64

    request.add_header("Authorization", "Basic " + base64.b64encode(credentials).decode("ascii"))
    request.add_header("Content-Type", "application/json")
    with _catc_open(request) as response:
        data = json.loads(response.read().decode("utf-8"))
    token = data.get("Token") or data.get("token")
    if not token:
        raise RuntimeError("Catalyst Center did not return an auth token")
    return token


def _catc_get(path: str, params: dict[str, str] | None = None, catalyst_connection: dict | None = None) -> dict:
    connection = catalyst_connection or {}
    host = str(connection.get("host") or os.environ.get("HOSTIP", "")).strip()
    if not host:
        raise RuntimeError("HOSTIP is not configured in the runner")
    query = "?" + urllib.parse.urlencode(params) if params else ""
    if not re.fullmatch(r"/dna/(?:intent|system)/api/v1/[A-Za-z0-9/_-]+", path):
        raise ValueError("Invalid Catalyst Center API path")
    request = urllib.request.Request(_catc_base_url(connection) + path + query)
    request.add_header("X-Auth-Token", _catc_token(connection))
    request.add_header("Content-Type", "application/json")
    with _catc_open(request) as response:
        return json.loads(response.read().decode("utf-8"))


def _interface_name(record: dict) -> str:
    for key in ("portName", "interfaceName", "name", "ifName"):
        value = record.get(key)
        if value:
            return str(value)
    return ""


def _device_by_management_ip(ip_address: str, catalyst_connection: dict | None = None) -> tuple[dict | None, str | None]:
    device_payload = _catc_get(
        "/dna/intent/api/v1/network-device",
        {"managementIpAddress": ip_address},
        catalyst_connection,
    )
    devices = device_payload.get("response") or []
    if not devices:
        return None, None
    device = devices[0]
    return device, device.get("id")


def _venv_python(venv_path: Path) -> Path:
    return venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _venv_ansible_playbook(venv_path: Path) -> Path:
    return venv_path / ("Scripts/ansible-playbook.exe" if os.name == "nt" else "bin/ansible-playbook")


def _resolve_venv(raw_path: str | None, *, must_exist: bool = False) -> Path | None:
    return _resolve_local_path(
        raw_path or str(DEFAULT_VENV),
        roots=(PROJECT_ROOT.resolve(), HOME_DIR),
        must_exist=must_exist,
    )


def _venv_status(venv_path: Path) -> dict:
    python_path = _venv_python(venv_path)
    ansible_path = _venv_ansible_playbook(venv_path)
    status = {
        "path": _display_path(venv_path),
        "absolute_path": str(venv_path),
        "python": str(python_path),
        "ansible_playbook": str(ansible_path),
        "requirements": _display_path(DEPENDENCY_REQUIREMENTS) if DEPENDENCY_REQUIREMENTS.exists() else "",
        "exists": venv_path.exists(),
        "python_exists": python_path.exists(),
        "ansible_playbook_exists": ansible_path.exists(),
        "ready": False,
        "missing": [],
    }
    if not python_path.exists():
        status["missing"].append("venv python")
    if not ansible_path.exists():
        status["missing"].append("ansible-playbook")

    if python_path.exists():
        for module in ("ansible", "catalystcentersdk", "yamale"):
            result = subprocess.run(
                [str(python_path), "-c", f"import {module}"],
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if result.returncode != 0:
                status["missing"].append(module)

    status["ready"] = not status["missing"]
    return status


def _candidate_venv_creators() -> list[str]:
    configured = os.environ.get("RUNNER_VENV_PYTHON")
    candidates = [configured] if configured else []
    candidates.extend(["python3.12", "python3", "python"])
    seen = set()
    return [item for item in candidates if item and not (item in seen or seen.add(item))]


def _create_venv(venv_path: Path) -> tuple[int, str, str]:
    if venv_path.exists() and _venv_python(venv_path).exists():
        return 0, "", "Venv already exists."

    attempts = []
    for executable in _candidate_venv_creators():
        cmd = [executable, "-m", "venv", str(venv_path)]
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        attempts.append("$ " + shlex.join(cmd) + "\n" + result.stdout)
        if result.returncode == 0 and _venv_python(venv_path).exists():
            return 0, shlex.join(cmd), "\n".join(attempts)

    return 1, "", "\n".join(attempts)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/jobs/<jid>")
def job_detail(jid):
    return render_template("job.html", job_id=jid)


@app.route("/api/workflows")
def api_workflows():
    return jsonify(_discover_workflows(PROJECT_ROOT))


@app.route("/api/inventories")
def api_inventories():
    return jsonify(_discover_inventories(PROJECT_ROOT))


@app.route("/api/device-interfaces", methods=["GET", "POST"])
def api_device_interfaces():
    data = request.get_json(silent=True) or {}
    ip_address = str(data.get("ip") or request.args.get("ip") or "").strip()
    catalyst_connection = data.get("catalyst_connection") if isinstance(data.get("catalyst_connection"), dict) else None
    if catalyst_connection and not catalyst_connection.get("enabled", True):
        catalyst_connection = None
    if not ip_address:
        return _json_error("Device IP is required")

    try:
        device, device_id = _device_by_management_ip(ip_address, catalyst_connection)
        if not device:
            return jsonify(ip=ip_address, device=None, interfaces=[])
        if not device_id:
            return _json_error("Catalyst Center device record has no id", 502)

        interface_payload = _catc_get(f"/dna/intent/api/v1/interface/network-device/{device_id}", catalyst_connection=catalyst_connection)
        interfaces = []
        seen_names = set()
        for record in interface_payload.get("response") or []:
            name = _interface_name(record)
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            interfaces.append(
                {
                    "name": name,
                    "adminStatus": record.get("adminStatus"),
                    "operStatus": record.get("status") or record.get("operStatus"),
                    "description": record.get("description"),
                    "vlanId": record.get("vlanId"),
                    "portMode": record.get("portMode"),
                    "interfaceType": record.get("interfaceType") or record.get("type"),
                }
            )
        interfaces.sort(key=lambda item: item["name"])
        return jsonify(
            ip=ip_address,
            device={
                "id": device_id,
                "hostname": device.get("hostname"),
                "managementIpAddress": device.get("managementIpAddress"),
                "collectionStatus": device.get("collectionStatus"),
                "reachabilityStatus": device.get("reachabilityStatus"),
            },
            interfaces=interfaces,
        )
    except urllib.error.HTTPError as exc:
        return _json_error(f"Catalyst Center request failed with HTTP {exc.code}", 502)
    except urllib.error.URLError:
        return _json_error("Could not reach Catalyst Center. Check server connectivity and TLS trust.", 502)
    except Exception:
        app.logger.exception("Device interface lookup failed")
        return _json_error("Unable to retrieve device interfaces. Check the runner server log.", 500)


@app.route("/api/host-port-assignments", methods=["GET", "POST"])
def api_host_port_assignments():
    data = request.get_json(silent=True) or {}
    ip_address = str(data.get("ip") or request.args.get("ip") or "").strip()
    catalyst_connection = data.get("catalyst_connection") if isinstance(data.get("catalyst_connection"), dict) else None
    if catalyst_connection and not catalyst_connection.get("enabled", True):
        catalyst_connection = None
    if not ip_address:
        return _json_error("Device IP is required")

    try:
        device, device_id = _device_by_management_ip(ip_address, catalyst_connection)
        if not device:
            return jsonify(ip=ip_address, device=None, assignments=[])
        if not device_id:
            return _json_error("Catalyst Center device record has no id", 502)

        assignment_payload = _catc_get(
            "/dna/intent/api/v1/sda/portAssignments",
            {"networkDeviceId": device_id, "limit": "500"},
            catalyst_connection,
        )
        assignments = []
        seen_names = set()
        for record in assignment_payload.get("response") or []:
            name = _interface_name(record)
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            assignments.append(
                {
                    "name": name,
                    "id": record.get("id"),
                    "connectedDeviceType": record.get("connectedDeviceType"),
                    "dataVlanName": record.get("dataVlanName"),
                    "voiceVlanName": record.get("voiceVlanName"),
                    "securityGroupName": record.get("securityGroupName"),
                    "authenticationTemplateName": record.get("authenticationTemplateName"),
                    "description": record.get("interfaceDescription") or record.get("description"),
                }
            )
        assignments.sort(key=lambda item: item["name"])
        return jsonify(
            ip=ip_address,
            device={
                "id": device_id,
                "hostname": device.get("hostname"),
                "managementIpAddress": device.get("managementIpAddress"),
                "collectionStatus": device.get("collectionStatus"),
                "reachabilityStatus": device.get("reachabilityStatus"),
            },
            assignments=assignments,
        )
    except urllib.error.HTTPError as exc:
        return _json_error(f"Catalyst Center request failed with HTTP {exc.code}", 502)
    except urllib.error.URLError:
        return _json_error("Could not reach Catalyst Center. Check server connectivity and TLS trust.", 502)
    except Exception:
        app.logger.exception("Host port assignment lookup failed")
        return _json_error("Unable to retrieve port assignments. Check the runner server log.", 500)


@app.route("/api/git/fetch", methods=["POST"])
def api_git_fetch():
    data = request.json or {}
    repo_url = str(data.get("repo_url") or "").strip()
    ref = str(data.get("ref") or "main").strip() or "main"
    if not repo_url:
        return _json_error("Git repository URL is required")
    repo_url, ref = _normalize_git_input(repo_url, ref)
    validation_error = _validate_git_input(repo_url, ref)
    if validation_error:
        return _json_error(validation_error)

    with _history_lock:
        lock = _repo_fetch_locks.setdefault((repo_url, ref), threading.Lock())
    if not lock.acquire(blocking=False):
        return _json_error("This repository is already being fetched. Refresh the catalog after it finishes.", 409)
    try:
        saved = _registered_repo(repo_url, ref)
        if saved and not data.get("refresh") and _resolve_git_source(saved["source"]) is not None:
            return jsonify(ok=True, source=saved["source"], vars=saved["vars"], inventories=saved["inventories"])
        return _fetch_git_snapshot(repo_url, ref)
    except (OSError, ValueError, sqlite3.Error):
        app.logger.error("Unable to fetch or register shared repository")
        return _json_error("Unable to fetch or save repository. Check server storage and Git access.", 503)
    finally:
        lock.release()


def _fetch_git_snapshot(repo_url, ref):

    source_id, target = _git_repo_cache_target()
    if not _is_within(target, GIT_REPOS_DIR.resolve()):
        return _json_error("Invalid repository target")

    GIT_REPOS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if target.exists() and (target / ".git").is_dir():
            checkout = _run_git_checkout(ref, target)
            if _git_lock_error(checkout.stdout):
                checkout = _clone_git_repo(repo_url, ref, target)
                if checkout.returncode != 0:
                    return _json_error(checkout.stdout, 500)
            else:
                if checkout.returncode != 0:
                    fetch = _run_git_fetch_ref(ref, target)
                    if _git_lock_error(fetch.stdout):
                        checkout = _clone_git_repo(repo_url, ref, target)
                        if checkout.returncode != 0:
                            return _json_error(checkout.stdout, 500)
                    elif fetch.returncode != 0:
                        return _json_error(fetch.stdout or checkout.stdout, 500)
                    else:
                        checkout = _run_git_checkout("FETCH_HEAD", target)
                        if checkout.returncode != 0:
                            return _json_error(checkout.stdout, 500)
                pull = _run_git_pull(target)
                if _git_lock_error(pull.stdout):
                    checkout = _clone_git_repo(repo_url, ref, target)
                    if checkout.returncode != 0:
                        return _json_error(checkout.stdout, 500)
                elif pull.returncode != 0:
                    fetch = _run_git_fetch_all(target)
                    if _git_lock_error(fetch.stdout):
                        checkout = _clone_git_repo(repo_url, ref, target)
                        if checkout.returncode != 0:
                            return _json_error(checkout.stdout, 500)
                    elif fetch.returncode != 0:
                        return _json_error(fetch.stdout or pull.stdout, 500)
        else:
            clone = _clone_git_repo(repo_url, ref, target)
            if clone.returncode != 0:
                return _json_error(clone.stdout, 500)

        commit = _run_git_head(target)
        source = {
            "kind": "git",
            "id": source_id,
            "repo_url": repo_url,
            "ref": ref,
            "commit": commit.stdout.strip() if commit.returncode == 0 else "",
        }
        record = dict(id=source_id, name=repo_url.rsplit("/", 1)[-1].removesuffix(".git"), source=source,
                      vars=_discover_repo_vars(target), inventories=_discover_inventories(target),
                      fetched_at=datetime.now(timezone.utc).isoformat())
        with _history_lock:
            connection = _repo_catalog_database()
            try:
                with connection:
                    connection.execute("INSERT OR REPLACE INTO git_repositories VALUES (?, ?, ?, ?)",
                                       (source_id, repo_url, ref, json.dumps(record)))
            finally:
                connection.close()
        return jsonify(ok=True, source=source, vars=record["vars"], inventories=record["inventories"])
    except subprocess.TimeoutExpired:
        return _json_error("Git operation timed out", 500)


@app.route("/api/fs")
def api_fs():
    root_info = _browse_root(request.args.get("root"))
    if root_info is None:
        return _json_error("Unknown browse root")

    root_label, root_path = root_info
    current, selected_file = _resolve_browse_target(root_path, request.args.get("path"))
    if current is None:
        return _json_error("Access denied or path not found", 403)

    directories = [
        {
            "name": entry.name,
            "path": str(entry),
        }
        for entry in _directories(current)
    ]
    files = [
        {
            "name": entry.name,
            "path": str(entry),
            "value": _display_path(entry),
        }
        for entry in _yaml_files(current)
    ]
    return jsonify(
        root=request.args.get("root", "repo").lower(),
        root_label=root_label,
        root_path=str(root_path),
        current_path=str(current),
        current_display=_display_path(current),
        parent_path=None if current == root_path else str(current.parent),
        breadcrumbs=_breadcrumbs(root_label, root_path, current),
        directories=directories,
        files=files,
        selected_file=_display_path(selected_file),
    )


@app.route("/api/file")
def api_read_file():
    source = None
    if request.args.get("source_kind") == "git":
        source = {"kind": "git", "id": request.args.get("source_id")}
    source_root = _resolve_git_source(source)
    if source_root is None:
        return _json_error("Git source not found")
    path = _resolve_source_file(request.args.get("path"), source_root, must_exist=True, allow_user_file=True)
    if path is None:
        return _json_error("Access denied or file not found", 403)
    if not path.is_file():
        return _json_error("Not found", 404)
    try:
        # codeql[py/path-injection] The resolver confines YAML files to their selected source.
        content = path.read_text(errors="replace")
    except OSError:
        app.logger.exception("Unable to read input file")
        return _json_error("Unable to read input file. Check the runner server log.", 500)
    return jsonify(path=_display_source_path(path, source_root), content=content)


@app.route("/api/file", methods=["PUT"])
def api_write_file():
    data = request.json or {}
    if not isinstance(data.get("content", ""), str):
        return _json_error("File content must be text")
    source_root = _resolve_git_source(data.get("source"))
    if source_root is None:
        return _json_error("Git source not found")
    path = _resolve_source_file(data.get("path"), source_root, must_exist=False, allow_user_file=True)
    if path is None:
        return _json_error("Access denied")
    try:
        # codeql[py/path-injection] The resolver confines YAML files to their selected source.
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data.get("content", ""))
    except OSError:
        app.logger.exception("Unable to save input file")
        return _json_error("Unable to save input file. Check the runner server log.", 500)
    return jsonify(status="saved", path=_display_source_path(path, source_root))


def _read_workflow_inputs(path: Path) -> dict:
    import yaml

    try:
        values = yaml.safe_load(path.read_text())
    except (yaml.YAMLError, UnicodeError) as exc:
        raise ValueError("Vars file must contain valid YAML") from exc
    if not isinstance(values, dict):
        raise ValueError("Vars file must contain a YAML mapping")
    return values


def _embedded_inventory(values: dict) -> dict:
    inventory = values.get("inventory")
    if not isinstance(inventory, dict) or not inventory:
        raise ValueError("Select an inventory file or add an inventory mapping to the vars file")
    seen = set()

    def check_group(group):
        if not isinstance(group, dict) or id(group) in seen:
            raise ValueError("Embedded inventory groups must be mappings without recursive aliases")
        seen.add(id(group))
        try:
            if set(group) - {"hosts", "children", "vars"}:
                raise ValueError("Embedded inventory groups support hosts, children, and vars")
            for field in ("hosts", "children", "vars"):
                if field in group and not isinstance(group[field], dict):
                    raise ValueError("Embedded inventory hosts, children, and vars must be mappings")
            hosts = group.get("hosts", {})
            for name, host_vars in hosts.items():
                if not isinstance(name, str) or not name.strip() or (host_vars is not None and not isinstance(host_vars, dict)):
                    raise ValueError("Embedded inventory hosts require names and variable mappings")
            count = len(hosts)
            for name, child in group.get("children", {}).items():
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("Embedded inventory groups require names")
                count += check_group(child)
            return count
        finally:
            seen.remove(id(group))

    count = 0
    for name, group in inventory.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Embedded inventory groups require names")
        count += check_group(group)
    if not count:
        raise ValueError("Embedded inventory must contain at least one host")
    return inventory


@app.route("/api/validate", methods=["POST"])
def api_validate():
    data = request.json or {}
    vars_source_root = _resolve_git_source(data.get("vars_source") or data.get("input_source") or data.get("source"))
    if vars_source_root is None:
        return _json_error("Git source not found")
    schema_path = _resolve_source_file(data.get("schema"), PROJECT_ROOT, must_exist=True, allow_user_file=False)
    vars_path = _resolve_source_file(
        data.get("data"),
        vars_source_root,
        must_exist=True,
        allow_user_file=True,
        allow_project_fallback=vars_source_root == PROJECT_ROOT.resolve(),
    )
    if schema_path is None:
        return _json_error("Schema file not found")
    if vars_path is None:
        return _json_error("Vars file not found")

    try:
        import yamale
        from yamale import YamaleError
    except ImportError:
        return _json_error("yamale is not installed in the runner environment", 500)

    try:
        schema = yamale.make_schema(str(schema_path))
        values = _read_workflow_inputs(vars_path)
        if "inventory" in values:
            _embedded_inventory(values)
            values = {key: value for key, value in values.items() if key != "inventory"}
        elif data.get("require_embedded_inventory"):
            return jsonify(ok=False, out="Select an inventory file or add an inventory mapping to the vars file")
        payload = [(values, str(vars_path))]
        yamale.validate(schema, payload)
        return jsonify(ok=True, out="Validation completed")
    except YamaleError as exc:
        details = []
        for result in exc.results:
            details.append(_display_path(Path(result.data)))
            details.extend(f"  - {error}" for error in result.errors)
        return jsonify(ok=False, out="\n".join(details))
    except ValueError:
        app.logger.exception("Invalid schema or workflow inputs")
        return jsonify(
            ok=False,
            out="Invalid schema or workflow inputs. Ensure the vars file contains a valid YAML mapping "
                "and select an inventory file or include a valid inventory mapping. "
                "Check the runner server log for details.",
        )
    except Exception:
        app.logger.exception("Schema validation failed unexpectedly")
        return _json_error("Unable to validate inputs. Check the runner server log.", 500)


@app.route("/api/environment")
def api_environment():
    venv_path = _resolve_venv(request.args.get("venv_path"), must_exist=False)
    if venv_path is None:
        return _json_error("Venv path must be inside the repository or your home directory")
    return jsonify(_venv_status(venv_path))


@app.route("/api/environment/create", methods=["POST"])
def api_environment_create():
    data = request.json or {}
    venv_path = _resolve_venv(data.get("venv_path"), must_exist=False)
    if venv_path is None:
        return _json_error("Venv path must be inside the repository or your home directory")

    rc, command, output = _create_venv(venv_path)
    status = _venv_status(venv_path)
    return jsonify(
        ok=rc == 0 and status["python_exists"],
        command=command,
        rc=rc,
        output=output,
        status=status,
    )


@app.route("/api/environment/setup", methods=["POST"])
def api_environment_setup():
    data = request.json or {}
    venv_path = _resolve_venv(data.get("venv_path"), must_exist=False)
    if venv_path is None:
        return _json_error("Venv path must be inside the repository or your home directory")

    python_path = _venv_python(venv_path)
    if not python_path.exists():
        rc, _, output = _create_venv(venv_path)
        if rc != 0 or not python_path.exists():
            return _json_error(f"Could not create venv at {venv_path}.\n{output}", 500)
    if not DEPENDENCY_REQUIREMENTS.exists():
        return _json_error("requirements.txt not found")

    cmd = [str(python_path), "-m", "pip", "install", "-r", str(DEPENDENCY_REQUIREMENTS)]
    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    status = _venv_status(venv_path)
    return jsonify(
        ok=result.returncode == 0 and status["ready"],
        command=shlex.join(cmd),
        rc=result.returncode,
        output=result.stdout,
        status=status,
    )


def _build_run_job(data: dict, *, kind: str = "single", batch_id: str = "", target: dict | None = None) -> tuple[Job | None, dict | str]:
    vars_source = data.get("vars_source") or data.get("input_source") or data.get("source") or {"kind": "local"}
    inventory_source = data.get("inventory_source") or data.get("input_source") or data.get("source") or {"kind": "local"}
    vars_source_root = _resolve_git_source(vars_source)
    inventory_source_root = _resolve_git_source(inventory_source)
    if vars_source_root is None or inventory_source_root is None:
        return None, "Git source not found"

    playbook_path = _resolve_source_file(data.get("playbook"), PROJECT_ROOT, must_exist=True, allow_user_file=False)
    inventory_path = _resolve_source_file(
        data.get("inventory"),
        inventory_source_root,
        must_exist=True,
        allow_user_file=True,
        allow_project_fallback=inventory_source_root == PROJECT_ROOT.resolve(),
    )
    vars_path = (
        _resolve_source_file(
            data.get("vars_file"),
            vars_source_root,
            must_exist=True,
            allow_project_fallback=vars_source_root == PROJECT_ROOT.resolve(),
        )
        if data.get("vars_file")
        else None
    )
    verbosity = data.get("verbosity", "")

    if playbook_path is None:
        return None, "Playbook not found"
    if inventory_path is None and data.get("inventory"):
        return None, "Inventory file not found"
    if vars_path is None and data.get("vars_file"):
        return None, "Vars file not found"
    if verbosity not in VERBOSITY_FLAGS:
        return None, "Unsupported verbosity flag"

    try:
        extra_args = shlex.split(data.get("extra_args", ""))
    except ValueError as exc:
        return None, f"Invalid extra arguments: {exc}"

    use_managed_venv = data.get("managed_venv", True)
    venv_path = _resolve_venv(data.get("venv_path"), must_exist=False)
    python_path = _venv_python(venv_path) if venv_path else None
    ansible_playbook = _venv_ansible_playbook(venv_path) if venv_path else None

    if use_managed_venv:
        if venv_path is None:
            return None, "Venv path must be inside the repository or your home directory"
        if not python_path or not python_path.exists():
            return None, f"Managed venv Python not found: {python_path}"
        if not ansible_playbook or not ansible_playbook.exists():
            return None, f"Managed venv ansible-playbook not found: {ansible_playbook}. Install dependencies first."

    embedded_inventory = None
    if inventory_path is None:
        if vars_path is None:
            return None, "Select an inventory file or a vars file containing inventory"
        try:
            embedded_inventory = _embedded_inventory(_read_workflow_inputs(vars_path))
        except (ValueError, OSError) as exc:
            return None, str(exc)

    executable = str(ansible_playbook) if use_managed_venv and ansible_playbook and ansible_playbook.exists() else "ansible-playbook"
    argv = [executable, "-i", str(inventory_path) if inventory_path else "<inventory from vars>", str(playbook_path)]
    if vars_path is not None:
        argv += ["--extra-vars", f"VARS_FILE_PATH={vars_path}"]
    if use_managed_venv and python_path and "ansible_python_interpreter" not in " ".join(extra_args):
        argv += ["--extra-vars", f"ansible_python_interpreter={python_path}"]
    if verbosity:
        argv.append(verbosity)
    argv.extend(extra_args)

    env_overrides = {}
    connection = data.get("catalyst_connection") or {}
    if connection.get("enabled"):
        if connection.get("host"):
            env_overrides["HOSTIP"] = str(connection["host"])
            env_overrides["CATALYST_CENTER_HOST"] = str(connection["host"])
        if connection.get("username"):
            env_overrides["CATALYST_CENTER_USERNAME"] = str(connection["username"])
        if connection.get("password"):
            env_overrides["CATALYST_CENTER_PASSWORD"] = str(connection["password"])
        if connection.get("verify"):
            env_overrides["CATALYST_CENTER_VERIFY"] = str(connection["verify"])

    target_name = str((target or {}).get("name") or "").strip()
    jid = data.get("_reserved_job_id") or uuid.uuid4().hex[:8]
    label = data.get("label") or playbook_path.stem
    if target_name:
        label = f"{label} · {target_name}"
    metadata = {
        "kind": kind,
        "batch_id": batch_id,
        "submitted_by": data.get("_submitted_by", ""),
        "suite_launch_id": data.get("suite_launch_id") or "",
        "suite_name": data.get("suite_name") or "",
        "suite_run_index": data.get("suite_run_index") or "",
        "suite_run_total": data.get("suite_run_total") or "",
        "suite_failure_policy": data.get("suite_failure_policy") or "",
        "suite_launch_mode": data.get("suite_launch_mode") or "",
        "suite_plan": data.get("suite_plan") if isinstance(data.get("suite_plan"), list) else [],
        "label": label,
        "target": {
            "name": target_name,
            "host": str(connection.get("host") or ""),
        } if target_name else {},
        "workflow": data.get("workflow") or "",
        "playbook": _display_source_path(playbook_path, PROJECT_ROOT),
        "inventory": _display_source_path(inventory_path, inventory_source_root) if inventory_path else "",
        "inventory_embedded": embedded_inventory is not None,
        "vars_file": _display_source_path(vars_path, vars_source_root) if vars_path is not None else "",
        "source": {"kind": "local"},
        "vars_source": vars_source,
        "inventory_source": inventory_source,
        "verbosity": verbosity,
        "extra_args": data.get("extra_args", ""),
        "managed_venv": use_managed_venv,
        "venv_path": data.get("venv_path") or "",
        "catalyst_connection_enabled": bool(connection.get("enabled")),
        "catalyst_connection_profile_id": str(connection.get("profile_id") or ""),
        "catalyst_connection_host": str(connection.get("host") or ""),
        "catalyst_connection_username": str(connection.get("username") or ""),
        "catalyst_connection_verify": str(connection.get("verify") or ""),
        "catalyst_connection_password_set": bool(connection.get("password")),
    }
    job = Job(jid, argv, str(PROJECT_ROOT), label, env_overrides, metadata)
    job.embedded_inventory = embedded_inventory
    job.capture_input_secrets((vars_path, inventory_path))
    return job, {"command": job.public_command()}


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.json or {}
    data.pop("_reserved_job_id", None)
    data["_submitted_by"] = _request_actor()
    job, result = _build_run_job(data, kind=data.get("kind") or "single")
    if job is None:
        return _json_error(str(result))
    with _jobs_lock:
        _jobs[job.id] = job
        _persist_job(job)
    threading.Thread(target=_exec, args=(job,), daemon=True).start()
    return jsonify(job_id=job.id, command=job.public_command())


def _exec_selected_suite_sequence(suites: list[dict], failure_policy: str):
    # Complete every play in a suite before advancing to the next suite.
    for suite in suites:
        _exec_suite_sequence(suite["runs"], failure_policy)


@app.route("/api/run/suites", methods=["POST"])
def api_run_suites():
    data = request.json or {}
    suites = data.get("suites")
    if not isinstance(suites, list) or not suites or any(
        not isinstance(suite, dict)
        or not isinstance(suite.get("runs"), list)
        or not suite["runs"]
        or any(not isinstance(run, dict) for run in suite["runs"])
        for suite in suites
    ):
        return _json_error("Select suites with at least one valid play each")
    failure_policy = "continue" if data.get("failure_policy") == "continue" else "stop"
    for suite in suites:
        _stamp_runs(suite["runs"])
    threading.Thread(
        target=_exec_selected_suite_sequence,
        args=(suites, failure_policy),
        daemon=True,
    ).start()
    return jsonify(accepted=len(suites), submitted=sum(len(suite["runs"]) for suite in suites))


@app.route("/api/run/suite", methods=["POST"])
def api_run_suite():
    data = request.json or {}
    runs = data.get("runs") or []
    if not isinstance(runs, list) or not runs or any(not isinstance(run, dict) for run in runs):
        return _json_error("Automation suite has no plays to launch")
    failure_policy = "continue" if data.get("failure_policy") == "continue" else "stop"
    _stamp_runs(runs)
    threading.Thread(target=_exec_suite_sequence, args=(runs, failure_policy), daemon=True).start()
    return jsonify(
        suite_launch_id=runs[0]["suite_launch_id"],
        submitted=len(runs),
        failure_policy=failure_policy,
    )


@app.route("/api/run/batch", methods=["POST"])
def api_run_batch():
    data = request.json or {}
    data.pop("_reserved_job_id", None)
    data["_submitted_by"] = _request_actor()
    targets = data.get("targets") or []
    if not isinstance(targets, list) or not targets:
        return _json_error("Select at least one Catalyst Center target")
    try:
        parallel_limit = max(1, min(8, int(data.get("parallel_limit") or 1)))
    except (TypeError, ValueError):
        return _json_error("Parallel limit must be a number from 1 to 8")

    batch_id = uuid.uuid4().hex[:8]
    jobs: list[Job] = []
    for index, target in enumerate(targets, start=1):
        if not isinstance(target, dict):
            return _json_error("Invalid Catalyst Center target")
        connection = target.get("connection") or {}
        run_data = dict(data)
        run_data["catalyst_connection"] = {
            "enabled": True,
            "host": connection.get("host") or target.get("host") or "",
            "username": connection.get("username") or target.get("username") or "",
            "password": connection.get("password") or target.get("password") or "",
            "verify": connection.get("verify") if connection.get("verify") is not None else target.get("verify", ""),
        }
        if target.get("vars_file"):
            run_data["vars_file"] = target.get("vars_file")
        if target.get("inventory"):
            run_data["inventory"] = target.get("inventory")
        run_data["label"] = data.get("label") or f"Batch {batch_id}"

        job, result = _build_run_job(run_data, kind="batch", batch_id=batch_id, target=target)
        if job is None:
            return _json_error(f"Target {index} ({target.get('name') or target.get('host') or 'unnamed'}): {result}")
        jobs.append(job)

    with _jobs_lock:
        for job in jobs:
            _jobs[job.id] = job
            _persist_job(job)
    semaphore = threading.Semaphore(parallel_limit)
    for job in jobs:
        threading.Thread(target=_exec_with_semaphore, args=(job, semaphore), daemon=True).start()

    return jsonify(
        batch_id=batch_id,
        jobs=[{"job_id": job.id, "label": job.label, "command": job.public_command(), "metadata": job.info()["metadata"]} for job in jobs],
    )


@app.route("/api/run/<jid>/stream")
def api_stream(jid):
    job = _jobs.get(jid)
    if not job:
        return _json_error("Not found", 404)

    try:
        index = max(0, int(request.args.get("start", "0")))
    except ValueError:
        return _json_error("Invalid stream offset")

    def gen():
        nonlocal index
        while True:
            with job._lock:
                chunk, status = job.lines[index:], job.status
            for line in chunk:
                yield f"data: {json.dumps(dict(t='o', l=line))}\n\n"
                index += 1
            if status in ("completed", "failed", "cancelled", "interrupted", "not-run"):
                yield f"data: {json.dumps(dict(t='d', s=status, rc=job.rc))}\n\n"
                break
            time.sleep(0.1)

    return Response(
        gen(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _cancel_job(job: Job) -> bool:
    with job._lock:
        if job.status not in ("queued", "running"):
            return False
        job.status = "cancelled"
        job.t1 = time.time()
        if job.proc:
            try:
                os.killpg(os.getpgid(job.proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        _persist_job(job)
        return True


@app.route("/api/run/<jid>/cancel", methods=["POST"])
def api_cancel(jid):
    job = _jobs.get(jid)
    if not job:
        return _json_error("Not found", 404)
    _cancel_job(job)
    return jsonify(status=job.status)


@app.route("/api/run/suite/<suite_id>/cancel", methods=["POST"])
def api_cancel_suite(suite_id):
    if not suite_id:
        return _json_error("Missing suite id")
    _cancelled_suites.add(suite_id)
    cancelled: list[str] = []
    with _jobs_lock:
        suite_jobs = [
            job for job in _jobs.values()
            if (job.metadata or {}).get("suite_launch_id") == suite_id
        ]
    for job in suite_jobs:
        if _cancel_job(job):
            cancelled.append(job.id)
    return jsonify(status="cancelled", suite_launch_id=suite_id, cancelled_jobs=cancelled)


@app.route("/api/jobs")
def api_jobs():
    with _jobs_lock:
        out = [_history_info(job) for job in _jobs.values()]
    out.sort(key=lambda item: item.get("t0") or 0, reverse=True)
    return jsonify(out)


@app.route("/api/jobs/<jid>")
def api_job(jid):
    job = _jobs.get(jid)
    if not job:
        return _json_error("Not found", 404)
    data = job.details()
    data["can_delete"] = _can_delete(job)
    return jsonify(data)


def _rerun_data(original):
    metadata = original.metadata
    if metadata.get("extra_args") or metadata.get("rerun_requires_options"):
        raise ValueError("This play used extra arguments that are not retained. Launch it manually with the required options.")
    data = {key: metadata.get(key, "") for key in ("workflow", "playbook", "vars_file", "inventory")}
    connection = {"enabled": bool(metadata.get("catalyst_connection_enabled") or metadata.get("catalyst_connection_host")),
                  "profile_id": metadata.get("catalyst_connection_profile_id", ""),
                  **{field: metadata.get("catalyst_connection_" + field, "") for field in ("host", "username", "verify")}}
    if metadata.get("vars_source"):
        data["vars_source"] = metadata["vars_source"]
        data["inventory_source"] = metadata.get("inventory_source") or metadata["vars_source"]
    else:
        # Older histories did not retain sources. Never guess a repository or target.
        with _suite_database() as database:
            suites = [json.loads(row[0]) for row in database.execute("SELECT data FROM saved_suites")]
        matches = [run for suite in suites if suite.get("name") == metadata.get("suite_name")
                   for run in suite.get("runs", [])
                   if all(run.get(field, "") == metadata.get(key, "") for field, key in
                          (("workflow", "workflow"), ("playbook", "playbook"), ("vars", "vars_file"), ("inventory", "inventory")))]
        if len(matches) != 1:
            raise ValueError("This older run has no unambiguous saved settings. Launch the play manually.")
        run = matches[0]
        repo = run.get("repo_details") or run.get("repoDetails") or {}
        source = repo.get("source")
        if not source and run.get("repo") not in ("local", "local-folder"):
            raise ValueError("The original input repository is unavailable. Launch the play manually.")
        data["vars_source"] = data["inventory_source"] = source or {"kind": "local"}
        target = run.get("target_details") or run.get("targetDetails")
        if run.get("target") and not target:
            raise ValueError("The original controller reference is unavailable. Launch the play manually.")
        connection = dict(target, enabled=True) if target else {"enabled": False}
    if not data["playbook"] or not data["vars_file"]:
        raise ValueError("The original play settings are incomplete. Launch the play manually.")
    if connection.get("enabled"):
        if not connection.get("profile_id"):
            raise ValueError("Save the original Catalyst Center connection before rerunning this play.")
        connection = _resolve_controller_reference(connection)
    data.update(catalyst_connection=connection, label=original.label + " retry",
                managed_venv=metadata.get("managed_venv", True),
                venv_path=metadata.get("venv_path", ""), verbosity=metadata.get("verbosity", ""),
                extra_args="", _submitted_by=_request_actor())
    return data


@app.post("/api/jobs/<jid>/rerun")
def api_rerun_job(jid):
    try:
        with _jobs_lock:
            original = _jobs.get(jid)
            if original is None:
                return _json_error("Not found", 404)
            if not _can_delete(original):
                return _json_error("Only the owner or an administrator can rerun a fully stopped play.", 403)
            if original.status != "failed":
                return _json_error("Only failed plays can be rerun.", 409)
            existing = _jobs.get(original.metadata.get("rerun_job_id"))
            if existing and existing.status in {"queued", "running"}:
                return jsonify(job_id=existing.id, rerun_of=jid, existing=True)
            data = _rerun_data(original)
            job, result = _build_run_job(data, kind="rerun")
            if job is None:
                return _json_error(str(result), 409)
            job.metadata["rerun_of"] = jid
            _jobs[job.id] = job
            _persist_job(job)
            original.metadata["rerun_job_id"] = job.id
            _persist_job(original)
            try:
                threading.Thread(target=_exec, args=(job,), daemon=True).start()
            except Exception:
                job.status, job.t1 = "failed", time.time()
                _persist_job(job)
                raise
        return jsonify(job_id=job.id, rerun_of=jid), 202
    except ValueError as error:
        return _json_error(str(error), 409)
    except Exception:
        app.logger.error("Unable to rerun failed play")
        return _json_error("Unable to rerun this play. Check saved settings and server storage.", 503)


def _request_actor():
    return (getattr(g, "runner_user", None) or {}).get("username", "")


def _stamp_runs(runs):
    suite_id = uuid.uuid4().hex
    plan = [{"index": index, **{key: run.get(key, "") for key in
             ("workflow", "playbook", "vars_file", "inventory")}}
            for index, run in enumerate(runs, start=1)]
    with _jobs_lock:
        for index, run in enumerate(runs, start=1):
            run["_submitted_by"] = _request_actor()
            run["suite_launch_id"] = run.get("suite_launch_id") or suite_id
            run["_reserved_job_id"] = uuid.uuid4().hex[:8]
            run["suite_run_index"] = run.get("suite_run_index") or index
            run["suite_run_total"] = len(runs)
            run["suite_plan"] = run.get("suite_plan") or plan
            metadata = _history_metadata(dict(run, submitted_by=_request_actor()))
            placeholder = Job(run["_reserved_job_id"], [], str(PROJECT_ROOT), run.get("label") or f"Play {index}", metadata=metadata)
            _jobs[placeholder.id] = placeholder
            _persist_job(placeholder)
            _active_suites.add(run["suite_launch_id"])


def _can_delete(job):
    user = getattr(g, "runner_user", None) or {}
    allowed = user.get("role") == "admin" or (
        user.get("role") == "operator" and bool(user.get("username"))
        and job.metadata.get("submitted_by") == user["username"])
    suite_id = job.metadata.get("suite_launch_id")
    suite_has_orphan = bool(suite_id and any(
        other.metadata.get("suite_launch_id") == suite_id and _process_exists(other.recovered_pid)
        for other in tuple(_jobs.values())))
    return bool(allowed and job.status in {"completed", "failed", "cancelled", "interrupted", "not-run"}
                and job.t1 is not None
                and job.metadata.get("suite_launch_id") not in _active_suites
                and not suite_has_orphan
                and not _process_exists(job.recovered_pid)
                and (job.proc is None or job.proc.poll() is not None))


def _process_exists(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _history_info(job):
    data = job.info()
    data["can_delete"] = _can_delete(job)
    return data


def _remaining_suite_metadata(metadata, removed):
    indices = {str(item.get("suite_run_index")) for item in removed}
    updated = dict(metadata)
    updated["suite_plan"] = [item for item in metadata.get("suite_plan", []) if str(item.get("index")) not in indices]
    updated["suite_run_total"] = max(0, int(metadata.get("suite_run_total") or 0) - len(removed))
    return updated


def _finish_history_deletion(root, request_id, ids):
    # The durable intent remains if file deletion or the final DB transaction fails.
    # Recompute from current records so overlapping/retried requests never double-count.
    if any(not isinstance(jid, str) or not re.fullmatch(r"[a-f0-9]{8}", jid) for jid in ids):
        raise ValueError("Invalid pending deletion identifier")
    with _history_connection(root) as connection:
        rows = {jid: json.loads(raw) for jid, raw in connection.execute("SELECT id,data FROM jobs")}
        removed = [data.get("metadata", {}) for jid, data in rows.items() if jid in ids]
        updates = {}
        for jid, data in rows.items():
            if jid in ids:
                continue
            metadata = data.get("metadata", {})
            matched = [item for item in removed if item.get("suite_launch_id")
                       and item["suite_launch_id"] == metadata.get("suite_launch_id")]
            if matched:
                data["metadata"] = _remaining_suite_metadata(metadata, matched)
                updates[jid] = data
        for jid in ids:
            (root / "logs" / (jid + ".jsonl")).unlink(missing_ok=True)
        for jid, data in updates.items():
            connection.execute("UPDATE jobs SET data=? WHERE id=?", (json.dumps(data), jid))
        for jid in ids:
            connection.execute("DELETE FROM jobs WHERE id=?", (jid,))
        connection.execute("DELETE FROM history_deletions WHERE id=?", (request_id,))
    return {jid: data["metadata"] for jid, data in updates.items()}


def _delete_history(jobs):
    # Caller holds _jobs_lock, excluding concurrent suite registration/deletion.
    user = getattr(g, "runner_user", None) or {}
    if any(user.get("role") != "admin" and job.metadata.get("submitted_by") != user.get("username")
           for job in jobs):
        return _json_error("You can only delete your own runs.", 403)
    if any(not _can_delete(job) for job in jobs):
        return _json_error("Stop the play and wait for its entire suite to finish before deleting history.", 409)
    root = _history_dir()
    deleted = {job.id for job in jobs}
    with _history_lock:
        if root is not None:
            encoded = json.dumps(sorted(deleted))
            request_id = hashlib.sha256(encoded.encode()).hexdigest()
            with _history_connection(root) as connection:
                connection.execute("INSERT OR IGNORE INTO history_deletions VALUES(?,?)", (request_id, encoded))
            updates = _finish_history_deletion(root, request_id, sorted(deleted))
        else:
            updates = {}
            for other in _jobs.values():
                removed = [job.metadata for job in jobs if job.metadata.get("suite_launch_id")
                           and job.metadata.get("suite_launch_id") == other.metadata.get("suite_launch_id")]
                if other.id not in deleted and removed:
                    updates[other.id] = _remaining_suite_metadata(other.metadata, removed)
        for jid, metadata in updates.items():
            if jid in _jobs:
                _jobs[jid].metadata = metadata
        for job in jobs:
            job._deleted = True
            _jobs.pop(job.id, None)
    return jsonify(deleted=sorted(deleted))


@app.delete("/api/jobs/<jid>")
def api_delete_job(jid):
    try:
        with _jobs_lock:
            job = _jobs.get(jid)
            if job is None:
                return _json_error("Not found", 404)
            return _delete_history([job])
    except (OSError, sqlite3.Error):
        app.logger.exception("Unable to delete job history")
        return _json_error("History deletion is pending. Fix storage permissions and retry, or restart to resume cleanup.", 503)


@app.delete("/api/suites/<suite_id>")
def api_delete_suite(suite_id):
    try:
        with _jobs_lock:
            jobs = [job for job in _jobs.values() if job.metadata.get("suite_launch_id") == suite_id]
            if not jobs:
                return _json_error("Not found", 404)
            return _delete_history(jobs)
    except (OSError, sqlite3.Error):
        app.logger.exception("Unable to delete suite history")
        return _json_error("History deletion is pending. Fix storage permissions and retry, or restart to resume cleanup.", 503)


@app.route("/api/jobs/<jid>/log")
def api_job_log(jid):
    job = _jobs.get(jid)
    if not job:
        return _json_error("Not found", 404)

    with job._lock:
        body = "".join(job.lines)

    return Response(
        body,
        mimetype="text/plain",
        headers={"Content-Disposition": f'inline; filename="{jid}.log"'},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def _clean_saved_suite(payload):
    if not isinstance(payload, dict):
        raise ValueError("Suite must be an object")
    name = payload.get("name")
    runs = payload.get("runs")
    if not isinstance(name, str) or not name.strip() or len(name) > 160:
        raise ValueError("Suite name must contain 1-160 characters")
    if not isinstance(runs, list) or not 1 <= len(runs) <= 100:
        raise ValueError("A suite must contain 1-100 plays")

    def strings(source, fields):
        result = {}
        for key in fields:
            value = source.get(key, "")
            if not isinstance(value, str) or len(value) > 2048:
                raise ValueError("Invalid suite field: " + key)
            result[key] = value
        return result

    cleaned = []
    for run in runs:
        if not isinstance(run, dict):
            raise ValueError("Each play must be an object")
        value = strings(run, ("name", "target", "repo", "workflow", "playbook", "vars", "inventory"))
        target = run.get("target_details") or run.get("targetDetails")
        if target:
            if not isinstance(target, dict):
                raise ValueError("Invalid controller reference")
            value["target_details"] = strings(target, ("name", "host", "username", "verify", "profile_id"))
        repo = run.get("repo_details") or run.get("repoDetails")
        if repo:
            if not isinstance(repo, dict) or not isinstance(repo.get("source"), dict):
                raise ValueError("Invalid repository reference")
            source = strings(repo["source"], ("kind", "id", "repo_url", "ref"))
            url = urlparse(source["repo_url"])
            if url.username or url.password or url.query or url.fragment:
                raise ValueError("Repository URLs must not contain credentials, queries or fragments")
            value["repo_details"] = {**strings(repo, ("id", "name")), "source": source}
        cleaned.append(value)
    return {"name": name.strip(), "runs": cleaned, "updatedAt": datetime.now(timezone.utc).isoformat()}


def _suite_response(row):
    sid, owner, revision, _, raw = row
    user = getattr(g, "runner_user", None) or {}
    editable = user.get("role") == "admin" or (user.get("role") == "operator" and owner == user.get("username"))
    return dict(json.loads(raw), id=sid, owner=owner, revision=revision, can_edit=editable, can_delete=editable)


def _suite_database():
    root = _history_dir()
    if root is None:
        raise sqlite3.OperationalError("Persistent storage required")
    return _history_connection(root)


@app.get("/api/git/catalog")
def saved_suite_repo_catalog():
    root = _resolve_git_source({"kind": "git", "id": request.args.get("source_id", "")})
    if root is None:
        return _json_error("Input repository is unavailable. Ask an administrator to fetch it on this server.", 404)
    return jsonify(vars=_discover_repo_vars(root), inventories=_discover_inventories(root))


@app.get("/api/saved-suites")
def saved_suites_list():
    try:
        with _history_lock, _suite_database() as connection:
            return jsonify([_suite_response(row) for row in connection.execute(
                "SELECT id,owner,revision,position,data FROM saved_suites ORDER BY position,id")])
    except (OSError, sqlite3.Error):
        app.logger.exception("Unable to read saved suites")
        return _json_error("Shared suites are unavailable. Check server storage.", 503)


@app.post("/api/saved-suites")
def saved_suite_create():
    try:
        payload = request.get_json(silent=True)
        suite = _clean_saved_suite(payload)
        owner = _request_actor()
        if not owner:
            return _json_error("Sign in required", 401)
        legacy = payload.get("legacy_id")
        if legacy is not None and (not isinstance(legacy, str) or not 1 <= len(legacy) <= 160):
            raise ValueError("Invalid browser import identifier")
        sid = uuid.uuid5(uuid.NAMESPACE_URL, owner + ":browser-suite:" + legacy).hex if legacy else uuid.uuid4().hex
        with _history_lock, _suite_database() as connection:
            existing = connection.execute("SELECT id,owner,revision,position,data FROM saved_suites WHERE id=?", (sid,)).fetchone()
            if existing:
                return jsonify(_suite_response(existing))
            position = connection.execute("SELECT COALESCE(MAX(position),-1)+1 FROM saved_suites").fetchone()[0]
            raw = json.dumps(suite)
            connection.execute("INSERT INTO saved_suites VALUES(?,?,1,?,?)", (sid, owner, position, raw))
        return jsonify(_suite_response((sid, owner, 1, position, raw))), 201
    except ValueError as error:
        return _json_error(str(error))
    except (OSError, sqlite3.Error):
        app.logger.exception("Unable to save suite")
        return _json_error("Unable to save shared suite. Check server storage.", 503)


def _change_saved_suite(sid, delete=False):
    try:
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict) or type(payload.get("revision")) is not int:
            raise ValueError("A suite revision is required")
        suite = None if delete else _clean_saved_suite(payload)
        with _history_lock, _suite_database() as connection:
            row = connection.execute("SELECT id,owner,revision,position,data FROM saved_suites WHERE id=?", (sid,)).fetchone()
            if not row:
                return _json_error("Saved suite not found", 404)
            if not _suite_response(row)["can_edit"]:
                return _json_error("Only the owner or an administrator can change this suite", 403)
            if row[2] != payload["revision"]:
                return _json_error("Suite changed in another session. Refresh before trying again.", 409)
            if delete:
                connection.execute("DELETE FROM saved_suites WHERE id=?", (sid,))
                return jsonify(deleted=sid)
            raw = json.dumps(suite)
            connection.execute("UPDATE saved_suites SET data=?,revision=revision+1 WHERE id=?", (raw, sid))
            return jsonify(_suite_response((sid, row[1], row[2] + 1, row[3], raw)))
    except ValueError as error:
        return _json_error(str(error))
    except (OSError, sqlite3.Error):
        app.logger.exception("Unable to change suite")
        return _json_error("Unable to change shared suite. Check server storage.", 503)


@app.put("/api/saved-suites/<sid>")
def saved_suite_update(sid):
    return _change_saved_suite(sid)


@app.delete("/api/saved-suites/<sid>")
def saved_suite_delete(sid):
    return _change_saved_suite(sid, delete=True)


@app.post("/api/saved-suites/order")
def saved_suite_reorder():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or any(not isinstance(item, dict) or not isinstance(item.get("id"), str) for item in items):
        return _json_error("Invalid suite order")
    try:
        with _history_lock, _suite_database() as connection:
            current = dict(connection.execute("SELECT id,revision FROM saved_suites"))
            ids = [item.get("id") for item in items]
            if len(ids) != len(set(ids)) or set(ids) != set(current) or any(
                    type(item.get("revision")) is not int or current.get(item["id"]) != item["revision"] for item in items):
                return _json_error("Suite list changed. Refresh before reordering.", 409)
            for position, sid in enumerate(ids):
                connection.execute("UPDATE saved_suites SET position=?,revision=revision+1 WHERE id=?", (position, sid))
        return jsonify(ok=True)
    except (OSError, sqlite3.Error):
        app.logger.exception("Unable to reorder suites")
        return _json_error("Unable to reorder shared suites.", 503)


if __name__ == "__main__":
    host = os.environ.get("RUNNER_HOST", "127.0.0.1")
    port = int(os.environ.get("RUNNER_PORT", "5005"))
    print("\n  Ansible Workflow Runner")
    print(f"  Project root : {PROJECT_ROOT}")
    print(f"  Workflows    : {WORKFLOWS_DIR}")
    print(f"  Inventory    : {INVENTORY_DIR}")
    print(f"  URL          : http://{host}:{port}\n")
    app.run(host=host, port=port, debug=False, threaded=True)
