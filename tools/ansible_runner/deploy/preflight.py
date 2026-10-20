#!/usr/bin/env python3
"""Non-mutating Linux readiness checks. Never prints credentials or runs playbooks."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]


def private_path(path, directory=False):
    if not path.exists() or path.is_dir() != directory:
        return False
    mode = stat.S_IMODE(path.stat().st_mode)
    return (mode & 0o077) == 0 and path.stat().st_uid == os.geteuid()


def directory_ready(path):
    # Check the nearest existing parent without creating directories or probe files.
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate.is_dir() and os.access(candidate, os.W_OK | os.X_OK)


def check_port():
    try:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 5005))
        return True
    except OSError:
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controller', help='Optional controller hostname/IP for a TCP-only check on port 443')
    args = parser.parse_args(argv)
    results = []

    def check(label, passed):
        results.append(bool(passed))
        print(('PASS' if passed else 'FAIL') + ': ' + label)

    check('Linux operating system', platform.system() == 'Linux')
    check('Python 3.12 or newer', sys.version_info >= (3, 12))
    check('Dedicated non-root service account', os.geteuid() != 0)
    check('Repository workflows directory', (ROOT / 'workflows').is_dir())
    check('Checkout writable for input edits and Git cache', os.access(ROOT, os.W_OK | os.X_OK))
    check('Git executable', shutil.which('git') is not None)
    check('Ansible executable in the current Python environment', (Path(sys.executable).parent / 'ansible-playbook').is_file())
    for module in ('flask', 'gunicorn', 'yamale', 'ansible', 'catalystcentersdk', 'sqlite3', 'cryptography.fernet'):
        try:
            result = subprocess.run([sys.executable, '-c',
                                     'import importlib,sys; importlib.import_module(sys.argv[1])', module],
                                    capture_output=True, text=True, timeout=30)
            check(module + ' imports successfully', result.returncode == 0)
        except (OSError, subprocess.TimeoutExpired):
            check(module + ' imports successfully', False)
    auth = Path(os.environ.get('RUNNER_AUTH_DIR', Path.home() / '.config/catalystcenter-runner')).expanduser()
    users = Path(os.environ.get('RUNNER_USERS_FILE', auth / 'users.json')).expanduser()
    check('Protected authentication directory owned by service account', private_path(auth, directory=True))
    check('Protected account file owned by service account', private_path(users))
    secret = os.environ.get('RUNNER_SECRET_KEY')
    try:
        if not secret:
            secret_file = auth / 'secret.key'
            secret = secret_file.read_text().strip() if private_path(secret_file) else ''
        check('Signing secret configured securely', len(secret) >= 32)
        accounts = json.loads(users.read_text())
        valid = isinstance(accounts, dict) and bool(accounts) and all(
            isinstance(user, dict) and user.get('role') in ('viewer', 'operator', 'admin')
            and isinstance(user.get('password_hash'), str) and user['password_hash'].startswith('scrypt:')
            and isinstance(user.get('enabled', True), bool) for user in accounts.values())
        check('Valid accounts with an enabled administrator', valid and any(
            user.get('role') == 'admin' and user.get('enabled', True) for user in accounts.values()))
    except (OSError, ValueError, TypeError):
        check('Readable account and signing-secret configuration', False)
    history = Path(os.environ.get('RUNNER_HISTORY_DIR', Path.home() / '.local/share/catalystcenter-runner')).expanduser().resolve()
    check('Dedicated writable history location', history not in (Path('/'), Path.home().resolve(), ROOT)
          and directory_ready(history))
    if history.exists():
        check('Protected history directory owned by service account', private_path(history, directory=True))
    for name in ('ANSIBLE_LOCAL_TEMP', 'ANSIBLE_REMOTE_TEMP'):
        value = os.environ.get(name)
        check(name + ' has a writable location', bool(value) and directory_ready(Path(value).expanduser()))
    check('Secure cookies enabled for future HTTPS access', os.environ.get('RUNNER_COOKIE_SECURE', 'true').lower() != 'false')
    check('Loopback listener port 5005 available', check_port())
    try:
        response = subprocess.run([str(Path(sys.executable).parent / 'ansible-galaxy'), 'collection', 'list',
                                   'cisco.catalystcenter', '--format', 'json'],
                                  capture_output=True, text=True, timeout=30)
        collections = json.loads(response.stdout) if response.returncode == 0 else {}
        check('cisco.catalystcenter collection installed', any(
            isinstance(value, dict) and 'cisco.catalystcenter' in value for value in collections.values()))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        check('cisco.catalystcenter collection installed', False)
    if args.controller:
        try:
            with socket.create_connection((args.controller, 443), timeout=5):
                check('Controller TCP port 443 reachable (not an API/authentication test)', True)
        except OSError:
            check('Controller TCP port 443 reachable', False)
    print('Preflight passed.' if all(results) else 'Preflight failed. Fix failed checks before starting the service.')
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
