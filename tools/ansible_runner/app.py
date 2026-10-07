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
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)

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

# In-memory job store (lost on restart — acceptable for a local tool)
_jobs: dict[str, "Job"] = {}
_jobs_lock = threading.Lock()


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
        self.status = "queued"
        self.lines: list[str] = []
        self.proc: subprocess.Popen | None = None
        self.t0: float | None = None
        self.t1: float | None = None
        self.rc: int | None = None
        self._lock = threading.Lock()

    def put(self, line: str):
        with self._lock:
            self.lines.append(line)

    def info(self):
        return dict(
            id=self.id,
            cmd=self.cmd,
            label=self.label,
            cwd=self.cwd,
            status=self.status,
            rc=self.rc,
            t0=self.t0,
            t1=self.t1,
            n=len(self.lines),
            metadata=self.metadata,
        )

    def details(self):
        with self._lock:
            lines = list(self.lines)
        data = self.info()
        data["lines"] = lines
        return data


def _exec(job: Job):
    """Execute ansible-playbook in a background thread."""
    job.status = "running"
    job.t0 = time.time()
    env = os.environ.copy()
    env["ANSIBLE_FORCE_COLOR"] = "true"
    env["PYTHONUNBUFFERED"] = "1"
    env.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
    env.setdefault("ANSIBLE_FORKS", "1")
    env.update(job.env_overrides)
    try:
        job.proc = subprocess.Popen(
            job.argv,
            cwd=job.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid,
            env=env,
        )
        if job.proc.stdout is not None:
            for line in iter(job.proc.stdout.readline, ""):
                job.put(line)
        job.proc.wait()
        job.rc = job.proc.returncode
        job.status = "completed" if job.rc == 0 else "failed"
    except Exception as exc:
        job.put(f"\n*** Error: {exc}\n")
        job.status = "failed"
    finally:
        job.t1 = time.time()


def _exec_with_semaphore(job: Job, semaphore: threading.Semaphore):
    with semaphore:
        _exec(job)


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

    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not any(_is_within(candidate, root) for root in roots):
        return None
    if must_exist and not candidate.exists():
        return None
    return candidate


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
        if allow_user_file:
            return _resolve_user_file(raw_path, must_exist=must_exist)
        return None

    source_candidate = _find_existing_relative_yaml(source_root, raw_path)
    if source_candidate and _is_within(source_candidate, source_root):
        return source_candidate
    if not must_exist:
        return None

    if allow_project_fallback and source_root != PROJECT_ROOT.resolve():
        project_candidate = _find_existing_relative_yaml(PROJECT_ROOT, raw_path)
        if project_candidate and _is_within(project_candidate, PROJECT_ROOT.resolve()):
            return project_candidate

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
        if "inventory" in lower_parts or lower_name.startswith("hosts."):
            continue
        if "schema" in lower_parts or "playbook" in lower_parts:
            continue
        if not ("vars" in lower_parts or "var" in lower_name or "input" in lower_name):
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

    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not _is_within(candidate, root):
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


def _catc_token(catalyst_connection: dict | None = None) -> str:
    """Return a Catalyst Center auth token without logging credentials."""
    connection = catalyst_connection or {}
    host = str(connection.get("host") or os.environ.get("HOSTIP", "")).strip()
    username = str(connection.get("username") or os.environ.get("CATALYST_CENTER_USERNAME", "")).strip()
    password = str(connection.get("password") or os.environ.get("CATALYST_CENTER_PASSWORD", ""))
    if not host or not username or not password:
        raise RuntimeError("Catalyst Center credentials are not configured in the runner")

    request = urllib.request.Request(f"https://{host}/dna/system/api/v1/auth/token", method="POST")
    credentials = f"{username}:{password}".encode("utf-8")
    import base64

    request.add_header("Authorization", "Basic " + base64.b64encode(credentials).decode("ascii"))
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, context=ssl._create_unverified_context(), timeout=30) as response:
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
    request = urllib.request.Request(f"https://{host}{path}{query}")
    request.add_header("X-Auth-Token", _catc_token(connection))
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, context=ssl._create_unverified_context(), timeout=30) as response:
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
    except urllib.error.URLError as exc:
        return _json_error(f"Could not reach Catalyst Center: {exc.reason}", 502)
    except Exception as exc:
        return _json_error(str(exc), 500)


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
    except urllib.error.URLError as exc:
        return _json_error(f"Could not reach Catalyst Center: {exc.reason}", 502)
    except Exception as exc:
        return _json_error(str(exc), 500)


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
        return jsonify(
            ok=True,
            source=source,
            vars=_discover_repo_vars(target),
            inventories=_discover_inventories(target),
        )
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
    # codeql[py/path-injection] path is resolved through _resolve_source_file and must remain inside an allowed root.
    return jsonify(path=_display_source_path(path, source_root), content=path.read_text(errors="replace"))


@app.route("/api/file", methods=["PUT"])
def api_write_file():
    data = request.json or {}
    source_root = _resolve_git_source(data.get("source"))
    if source_root is None:
        return _json_error("Git source not found")
    path = _resolve_source_file(data.get("path"), source_root, must_exist=False, allow_user_file=True)
    if path is None:
        return _json_error("Access denied")
    # codeql[py/path-injection] path is resolved through _resolve_source_file and must remain inside an allowed root.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data.get("content", ""))
    return jsonify(status="saved", path=_display_source_path(path, source_root))


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
        payload = yamale.make_data(str(vars_path))
        yamale.validate(schema, payload)
        return jsonify(ok=True, out="Validation completed")
    except YamaleError as exc:
        details = []
        for result in exc.results:
            details.append(_display_path(Path(result.data)))
            details.extend(f"  - {error}" for error in result.errors)
        return jsonify(ok=False, out="\n".join(details))
    except Exception as exc:
        return _json_error(str(exc), 500)


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
    if inventory_path is None:
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

    executable = str(ansible_playbook) if use_managed_venv and ansible_playbook and ansible_playbook.exists() else "ansible-playbook"
    argv = [executable, "-i", str(inventory_path), str(playbook_path)]
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
    jid = uuid.uuid4().hex[:8]
    label = data.get("label") or playbook_path.stem
    if target_name:
        label = f"{label} · {target_name}"
    metadata = {
        "kind": kind,
        "batch_id": batch_id,
        "suite_launch_id": data.get("suite_launch_id") or "",
        "suite_name": data.get("suite_name") or "",
        "suite_run_index": data.get("suite_run_index") or "",
        "suite_run_total": data.get("suite_run_total") or "",
        "suite_plan": data.get("suite_plan") if isinstance(data.get("suite_plan"), list) else [],
        "label": label,
        "target": {
            "name": target_name,
            "host": str(connection.get("host") or ""),
        } if target_name else {},
        "workflow": data.get("workflow") or "",
        "playbook": _display_source_path(playbook_path, PROJECT_ROOT),
        "inventory": _display_source_path(inventory_path, inventory_source_root),
        "vars_file": _display_source_path(vars_path, vars_source_root) if vars_path is not None else "",
        "source": {"kind": "local"},
        "vars_source": vars_source,
        "inventory_source": inventory_source,
        "verbosity": verbosity,
        "extra_args": data.get("extra_args", ""),
        "managed_venv": use_managed_venv,
        "venv_path": data.get("venv_path") or "",
        "catalyst_connection_enabled": bool(connection.get("enabled")),
        "catalyst_connection_host": str(connection.get("host") or ""),
        "catalyst_connection_username": str(connection.get("username") or ""),
        "catalyst_connection_verify": str(connection.get("verify") or ""),
        "catalyst_connection_password_set": bool(connection.get("password")),
    }
    job = Job(jid, argv, str(PROJECT_ROOT), label, env_overrides, metadata)
    return job, {"command": job.cmd}


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.json or {}
    job, result = _build_run_job(data, kind=data.get("kind") or "single")
    if job is None:
        return _json_error(str(result))
    with _jobs_lock:
        _jobs[job.id] = job
    threading.Thread(target=_exec, args=(job,), daemon=True).start()
    return jsonify(job_id=job.id, command=job.cmd)


@app.route("/api/run/batch", methods=["POST"])
def api_run_batch():
    data = request.json or {}
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
    semaphore = threading.Semaphore(parallel_limit)
    for job in jobs:
        threading.Thread(target=_exec_with_semaphore, args=(job, semaphore), daemon=True).start()

    return jsonify(
        batch_id=batch_id,
        jobs=[{"job_id": job.id, "label": job.label, "command": job.cmd, "metadata": job.metadata} for job in jobs],
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
            if status in ("completed", "failed", "cancelled"):
                yield f"data: {json.dumps(dict(t='d', s=status, rc=job.rc))}\n\n"
                break
            time.sleep(0.1)

    return Response(
        gen(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/run/<jid>/cancel", methods=["POST"])
def api_cancel(jid):
    job = _jobs.get(jid)
    if not job:
        return _json_error("Not found", 404)
    if job.proc and job.status == "running":
        try:
            os.killpg(os.getpgid(job.proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        job.status = "cancelled"
    return jsonify(status=job.status)


@app.route("/api/jobs")
def api_jobs():
    with _jobs_lock:
        out = [job.info() for job in _jobs.values()]
    out.sort(key=lambda item: item.get("t0") or 0, reverse=True)
    return jsonify(out)


@app.route("/api/jobs/<jid>")
def api_job(jid):
    job = _jobs.get(jid)
    if not job:
        return _json_error("Not found", 404)
    return jsonify(job.details())


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
if __name__ == "__main__":
    host = os.environ.get("RUNNER_HOST", "127.0.0.1")
    port = int(os.environ.get("RUNNER_PORT", "5005"))
    print("\n  Ansible Workflow Runner")
    print(f"  Project root : {PROJECT_ROOT}")
    print(f"  Workflows    : {WORKFLOWS_DIR}")
    print(f"  Inventory    : {INVENTORY_DIR}")
    print(f"  URL          : http://{host}:{port}\n")
    app.run(host=host, port=port, debug=True, threaded=True)
