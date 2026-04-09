#!/usr/bin/env python3
"""Ansible Workflow Runner backend."""

import json
import os
import shlex
import signal
import subprocess
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)

# Project root is two levels up: tools/ansible_runner/app.py -> repo root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / "workflows"
INVENTORY_DIR = PROJECT_ROOT / "inventory"
HOME_DIR = Path.home().resolve()
YAML_SUFFIXES = {".yml", ".yaml"}
VERBOSITY_FLAGS = {"", "-v", "-vv", "-vvv", "-vvvv"}
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

    def __init__(self, jid: str, argv: list[str], cwd: str, label: str = ""):
        self.id = jid
        self.argv = argv
        self.cmd = shlex.join(argv)
        self.cwd = cwd
        self.label = label
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
    out = []
    if not WORKFLOWS_DIR.is_dir():
        return jsonify(out)

    for directory in sorted(WORKFLOWS_DIR.iterdir()):
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

    return jsonify(out)


@app.route("/api/inventories")
def api_inventories():
    out = []
    if not INVENTORY_DIR.is_dir():
        return jsonify(out)

    for root, _dirs, files in os.walk(INVENTORY_DIR):
        for filename in files:
            if filename.endswith((".yml", ".yaml")):
                out.append(os.path.relpath(os.path.join(root, filename), PROJECT_ROOT))
    return jsonify(sorted(out))


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
    path = _resolve_user_file(request.args.get("path"), must_exist=True)
    if path is None:
        return _json_error("Access denied or file not found", 403)
    if not path.is_file():
        return _json_error("Not found", 404)
    return jsonify(path=_display_path(path), content=path.read_text(errors="replace"))


@app.route("/api/file", methods=["PUT"])
def api_write_file():
    data = request.json or {}
    path = _resolve_user_file(data.get("path"), must_exist=False)
    if path is None:
        return _json_error("Access denied")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data.get("content", ""))
    return jsonify(status="saved", path=_display_path(path))


@app.route("/api/validate", methods=["POST"])
def api_validate():
    data = request.json or {}
    schema_path = _resolve_repo_path(data.get("schema"), must_exist=True)
    vars_path = _resolve_user_file(data.get("data"), must_exist=True)
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


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.json or {}

    playbook_path = _resolve_repo_path(data.get("playbook"), must_exist=True)
    inventory_path = _resolve_user_file(data.get("inventory"), must_exist=True)
    vars_path = _resolve_user_file(data.get("vars_file"), must_exist=True) if data.get("vars_file") else None
    verbosity = data.get("verbosity", "")

    if playbook_path is None:
        return _json_error("Playbook not found")
    if inventory_path is None:
        return _json_error("Inventory file not found")
    if vars_path is None and data.get("vars_file"):
        return _json_error("Vars file not found")
    if verbosity not in VERBOSITY_FLAGS:
        return _json_error("Unsupported verbosity flag")

    try:
        extra_args = shlex.split(data.get("extra_args", ""))
    except ValueError as exc:
        return _json_error(f"Invalid extra arguments: {exc}")

    argv = ["ansible-playbook", "-i", str(inventory_path), str(playbook_path)]
    if vars_path is not None:
        argv += ["--extra-vars", f"VARS_FILE_PATH={vars_path}"]
    if verbosity:
        argv.append(verbosity)
    argv.extend(extra_args)

    jid = uuid.uuid4().hex[:8]
    label = data.get("label") or playbook_path.stem
    job = Job(jid, argv, str(PROJECT_ROOT), label)
    with _jobs_lock:
        _jobs[jid] = job
    threading.Thread(target=_exec, args=(job,), daemon=True).start()
    return jsonify(job_id=jid, command=job.cmd)


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
