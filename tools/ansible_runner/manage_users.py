#!/usr/bin/env python3
"""Manage local runner accounts. Run as the runner's service account."""
import argparse
import getpass
import json
import os
import re
import secrets
import tempfile
from pathlib import Path
from werkzeug.security import generate_password_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "set", "disable"])
    parser.add_argument("username")
    parser.add_argument("--role", choices=["viewer", "operator", "admin"], default="viewer")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", args.username):
        parser.error("Use 1-64 letters, digits, dots, underscores or hyphens for the username.")
    root = Path(os.environ.get("RUNNER_AUTH_DIR", Path.home() / ".config/catalystcenter-runner"))
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = Path(os.environ.get("RUNNER_USERS_FILE", str(root / "users.json")))
    users = json.loads(path.read_text()) if path.exists() else {}
    if args.action == "init" and users:
        parser.error("Already initialized; use set to update accounts.")
    if args.action == "disable":
        if args.username not in users:
            parser.error("Unknown account.")
        users[args.username]["enabled"] = False
    else:
        password = getpass.getpass("Password (minimum 5 characters): ")
        if len(password) < 5 or password != getpass.getpass("Confirm password: "):
            parser.error("Passwords must match and contain at least 5 characters.")
        users[args.username] = {"password_hash": generate_password_hash(password),
                                "role": "admin" if args.action == "init" else args.role, "enabled": True}
    if not any(user.get("enabled", True) and user["role"] == "admin" for user in users.values()):
        parser.error("At least one enabled administrator is required.")
    if not (root / "secret.key").exists():
        with open(root / "secret.key", "x", opener=lambda p, f: os.open(p, f, 0o600)) as secret:
            secret.write(secrets.token_urlsafe(48))
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as output:
            json.dump(users, output, indent=2)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("Account configuration saved. Restart the runner after initial setup.")


if __name__ == "__main__":
    main()
