#!/usr/bin/env python3
"""Ansible Workflow Runner backend."""

import json
import os
import shlex
import signal
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

APP_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(APP_DIR / "templates"))
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Project root is two levels up: tools/ansible_runner/app.py -> repo root
PROJECT_ROOT = APP_DIR.parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / "workflows"
INVENTORY_DIR = PROJECT_ROOT / "inventory"
HOME_DIR = Path.home().resolve()
YAML_SUFFIXES = {".yml", ".yaml"}
VERBOSITY_FLAGS = {"", "-v", "-vv", "-vvv", "-vvvv"}
ANSIBLE_PLAYBOOK_BIN = os.environ.get(
    "ANSIBLE_PLAYBOOK_BIN",
    "ansible-playbook",
)
ANSIBLE_PYTHON = os.environ.get(
    "ANSIBLE_PYTHON_INTERPRETER",
    sys.executable,
)
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
    env = _runtime_env()
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


def _runtime_env() -> dict[str, str]:
    """Build the environment used by every UI-launched Ansible job."""
    env = os.environ.copy()
    env["ANSIBLE_FORCE_COLOR"] = "true"
    env["PYTHONUNBUFFERED"] = "1"
    runner_tmp = Path(
        env.get("RUNNER_TMPDIR", "/tmp/catalystcenter-ansible-runner")
    ).resolve()
    runner_tmp.mkdir(parents=True, exist_ok=True)
    env.setdefault("ANSIBLE_LOCAL_TEMP", str(runner_tmp))
    env.setdefault("ANSIBLE_REMOTE_TEMP", str(runner_tmp / "remote"))
    env.setdefault("ANSIBLE_ROLES_PATH", str(PROJECT_ROOT / "roles"))
    env.setdefault("ANSIBLE_PYTHON_INTERPRETER", ANSIBLE_PYTHON)
    env["PWD"] = str(PROJECT_ROOT)

    collection_paths = [
        PROJECT_ROOT / "collections",
        PROJECT_ROOT / ".ansible" / "collections",
        PROJECT_ROOT,
        HOME_DIR / ".ansible" / "collections",
    ]
    configured = [
        item for item in env.get("ANSIBLE_COLLECTIONS_PATH", "").split(os.pathsep)
        if item
    ]
    configured.extend(str(path) for path in collection_paths if path.exists())
    env["ANSIBLE_COLLECTIONS_PATH"] = os.pathsep.join(dict.fromkeys(configured))
    return env


def _runtime_readiness() -> dict[str, dict[str, bool]]:
    """Return safe boolean status without exposing credential values."""
    groups = {
        "catalyst_center": (
            "HOSTIP",
            "CATALYST_CENTER_USERNAME",
            "CATALYST_CENTER_PASSWORD",
        ),
        "switch_credentials": (
            "SWITCH_CLI_USERNAME",
            "SWITCH_CLI_PASSWORD",
            "SWITCH_ENABLE_PASSWORD",
        ),
        "snmpv3_credentials": (
            "SNMPV3_USERNAME",
            "SNMPV3_AUTH_PASSWORD",
            "SNMPV3_PRIV_PASSWORD",
        ),
    }
    return {
        group: {name: bool(os.environ.get(name, "").strip()) for name in names}
        for group, names in groups.items()
    }


def _catc_token() -> str:
    """Return a Catalyst Center auth token without logging credentials."""
    host = os.environ.get("HOSTIP", "").strip()
    username = os.environ.get("CATALYST_CENTER_USERNAME", "").strip()
    password = os.environ.get("CATALYST_CENTER_PASSWORD", "")
    if not host or not username or not password:
        raise RuntimeError("Catalyst Center credentials are not configured in the runner")

    url = f"https://{host}/dna/system/api/v1/auth/token"
    request = urllib.request.Request(url, method="POST")
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


def _catc_get(path: str, params: dict[str, str] | None = None) -> dict:
    host = os.environ.get("HOSTIP", "").strip()
    if not host:
        raise RuntimeError("HOSTIP is not configured in the runner")
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(f"https://{host}{path}{query}")
    request.add_header("X-Auth-Token", _catc_token())
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, context=ssl._create_unverified_context(), timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _interface_name(record: dict) -> str:
    for key in ("portName", "interfaceName", "name", "ifName"):
        value = record.get(key)
        if value:
            return str(value)
    return ""


def _device_by_management_ip(ip_address: str) -> tuple[dict | None, str | None]:
    device_payload = _catc_get(
        "/dna/intent/api/v1/network-device",
        {"managementIpAddress": ip_address},
    )
    devices = device_payload.get("response") or []
    if not devices:
        return None, None
    device = devices[0]
    return device, device.get("id")


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


@app.route("/api/runtime")
def api_runtime():
    """Expose non-secret runner readiness details to the guided UI."""
    return jsonify(
        ansible_playbook=ANSIBLE_PLAYBOOK_BIN,
        project_root=str(PROJECT_ROOT),
        readiness=_runtime_readiness(),
    )


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


@app.route("/api/device-interfaces")
def api_device_interfaces():
    ip_address = (request.args.get("ip") or "").strip()
    if not ip_address:
        return _json_error("Device IP is required")

    try:
        device, device_id = _device_by_management_ip(ip_address)
        if not device:
            return jsonify(ip=ip_address, device=None, interfaces=[])
        if not device_id:
            return _json_error("Catalyst Center device record has no id", 502)

        interface_payload = _catc_get(
            f"/dna/intent/api/v1/interface/network-device/{device_id}"
        )
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


@app.route("/api/host-port-assignments")
def api_host_port_assignments():
    ip_address = (request.args.get("ip") or "").strip()
    if not ip_address:
        return _json_error("Device IP is required")

    try:
        device, device_id = _device_by_management_ip(ip_address)
        if not device:
            return jsonify(ip=ip_address, device=None, assignments=[])
        if not device_id:
            return _json_error("Catalyst Center device record has no id", 502)

        assignment_payload = _catc_get(
            "/dna/intent/api/v1/sda/portAssignments",
            {"networkDeviceId": device_id, "limit": "500"},
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

    is_switch_refresh = playbook_path.parent.parent.name == "switch_refresh"
    is_syntax_check = "--syntax-check" in extra_args
    if is_switch_refresh and vars_path is None:
        return _json_error(
            "Select a switch-refresh vars file before launching this playbook. "
            "Use workflows/switch_refresh/vars/switch_refresh_usecase.yml for "
            "full flow and cleanup runs."
        )
    if is_switch_refresh and not is_syntax_check:
        readiness = _runtime_readiness()
        missing = [
            name
            for name, present in readiness["catalyst_center"].items()
            if not present
        ]
        if playbook_path.name in {"switch_refresh_prepare.yml", "switch_refresh_full_flow.yml"}:
            missing.extend(
                name
                for name, present in readiness["switch_credentials"].items()
                if not present
            )
        if missing:
            return _json_error(
                "Runner is missing required Catalyst Center settings: "
                + ", ".join(missing)
                + ". Restart it with start_switch_refresh_runner.sh so it "
                "loads the target and prompts for credentials.",
                503,
            )

    argv = [ANSIBLE_PLAYBOOK_BIN, "-i", str(inventory_path), str(playbook_path)]
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
    port = int(os.environ.get("RUNNER_PORT", "5006"))
    debug = os.environ.get("RUNNER_DEBUG", "false").lower() in {"1", "true", "yes", "on"}
    print("\n  Ansible Workflow Runner")
    print(f"  Project root : {PROJECT_ROOT}")
    print(f"  Workflows    : {WORKFLOWS_DIR}")
    print(f"  Inventory    : {INVENTORY_DIR}")
    print(f"  Ansible      : {ANSIBLE_PLAYBOOK_BIN}")
    print(f"  URL          : http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug, threaded=True)
