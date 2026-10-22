# Linux preparation (private backend only)

These files do not deploy anything by themselves. No SSH, firewall, NGINX,
HTTPS certificate, or public/team listener is configured in this stage.
The sole application listener is **127.0.0.1:5005**. Team access and its port
will be configured separately. Secure cookies stay enabled; direct HTTP browser
login is intentionally not a supported shared-access deployment.

## Files

- `requirements-linux.txt`: Flask/Yamale plus Gunicorn, separate from local dependencies.
- `gunicorn.conf.py`: one gthread worker with 16 threads, stdout/stderr logging.
- `catalystcenter-runner.service`: non-root systemd service and shutdown controls.
- `runner.env.example`: path configuration, containing no passwords.
- `preflight.py`: checks only; no package installs, file writes or playbook execution.

## Planned layout

| Path | Purpose |
| --- | --- |
| `/srv/catalystcenter-runner/app` | Repository checkout and `.venv312` Python environment |
| `/etc/catalystcenter-runner/runner.env` | Root-managed environment file (0640, group catalyst-runner) |
| `/var/lib/catalystcenter-runner/auth` | Users and signing secret (0700 directory, 0600 files) |
| `/var/lib/catalystcenter-runner/history` | Persistent SQLite metadata and protected logs |
| `/var/lib/catalystcenter-runner/.ansible` | Service account's Ansible collections |

Use the dedicated `catalyst-runner` user and group. The application can edit YAML,
fetch repositories and create its execution environment, so this pilot's checkout
must be writable by that trusted service account. Do not use its home or checkout
for unrelated credentials. Changing paths requires updating both the environment
template and unit file. Put custom inventories and input repositories under the
checkout or the service account's home, not a developer's `/Users/...` path.

## Later server setup

Run these only after confirming the Linux OS and approving installation.
Prerequisites: systemd, Git, Python 3.12 with venv/pip support, the service account,
and an approved checkout containing these changes. Do not copy a macOS virtual
environment to Linux. Create the checkout and state directories with service
account ownership; keep `/etc/catalystcenter-runner` root-managed.

Example administrative directory preparation (assumes user/group already exist):

```sh
sudo install -d -m 0750 -o root -g catalyst-runner /etc/catalystcenter-runner
sudo install -d -m 0700 -o catalyst-runner -g catalyst-runner /var/lib/catalystcenter-runner
sudo install -d -m 0750 -o catalyst-runner -g catalyst-runner /srv/catalystcenter-runner
```

After placing the repository at `/srv/catalystcenter-runner/app`, prepare the
environment as `catalyst-runner` (with `HOME=/var/lib/catalystcenter-runner`):

```sh
cd /srv/catalystcenter-runner/app
python3.12 -m venv .venv312
.venv312/bin/python -m pip install -r requirements.txt -r tools/ansible_runner/deploy/requirements-linux.txt
.venv312/bin/ansible-galaxy collection install cisco.catalystcenter
RUNNER_AUTH_DIR=/var/lib/catalystcenter-runner/auth \
  .venv312/bin/python tools/ansible_runner/manage_users.py init admin
```

Use a collection version approved for the lab; record tested package/collection
versions before the demo. Provide the admin password at the prompt, never in a
command, environment template, Git commit or recording.

As the administrator, copy the supplied environment template to
`/etc/catalystcenter-runner/runner.env` with root:catalyst-runner ownership and
mode 0640. Review its paths before installation. This file uses simple
`NAME=value` assignments compatible with systemd's `EnvironmentFile`.

For a manual preflight, run as the service account with the same HOME, source
the reviewed environment file in a shell using `set -a`, then run:

```sh
.venv312/bin/python tools/ansible_runner/deploy/preflight.py
# Optional TCP-only controller check, no credentials or configuration changes:
.venv312/bin/python tools/ansible_runner/deploy/preflight.py --controller CONTROLLER_HOST
.venv312/bin/gunicorn --check-config --config tools/ansible_runner/deploy/gunicorn.conf.py tools.ansible_runner.app:app
```

The preflight intentionally fails on macOS, under root, or when the private
listener is already occupied. It checks actual Python imports, not just installed
package names. Run it before starting the service, not while that service already
owns the listener. It does not authenticate to Catalyst Center, check private Git
access, validate certificates, or verify workflow inputs. Those remain rehearsal
checks. It briefly binds and releases the loopback socket, but never serves data.

Review and install the unit as `/etc/systemd/system/catalystcenter-runner.service`.
Before enabling it, validate it on the actual server:

```sh
sudo systemd-analyze verify /etc/systemd/system/catalystcenter-runner.service
sudo systemctl daemon-reload
sudo systemctl enable --now catalystcenter-runner
sudo systemctl status catalystcenter-runner
sudo journalctl -u catalystcenter-runner -n 100 --no-pager
```

Do not run a development server alongside the service. Do not override the
single-worker setting or enable preload, auto-reload, or worker recycling.
Sessions, cancellation and live process handles are still process-local.
Multiple workers or services sharing the same history directory are unsupported.
The threads also service live log streams; 16 threads is not a promise of 16
concurrent playbooks or unlimited viewers.

## Shutdown and restart

`KillMode=control-group` applies stop signals to the web processes and child
Ansible processes, including children started in a new process session. The stop
timeout is longer than Gunicorn's graceful timeout. A service restart can interrupt
playbooks: do not restart during an active demo/run. Interrupting Ansible does not
undo a controller operation that was already submitted. History marks unfinished
work interrupted on the next startup; no automatic rerun occurs. Stopping a
manually launched development server does not provide the systemd cleanup guarantee.

## Before recording

After HTTPS/team access is configured separately, verify login/roles, sequential
suites, cancellation, live and saved logs, and ownership-protected deletion.
With no active network-changing runs, restart once and confirm history persists.
Verify Git access, input paths and Catalyst Center connectivity as the service
account. Keep credentials out of screenshots and logs. External frontend CDNs
must be reachable from viewers' browsers; these templates do not bundle them.

On RHEL, check SELinux denials and approved file labels/policy rather than
disabling SELinux. Confirm systemd supports the supplied hardening directives.
Monitor disk usage and back up the database/logs together while stopped.
