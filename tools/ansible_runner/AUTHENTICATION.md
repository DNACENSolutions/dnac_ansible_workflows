# Login and permissions

Local accounts are a first deployment stage, not company SSO. Authentication is
required by default. Missing or invalid account/secret configuration returns 503;
there is no default account or production authentication bypass.

## Initial setup

From the repository root, using the runner's Python environment and the same OS
service account that will run the application:

```sh
python tools/ansible_runner/manage_users.py init admin
```

Enter a unique password at the prompts (at least 5 characters). Use a long,
unique password for shared deployments; the minimum is not a security recommendation. This creates
`~/.config/catalystcenter-runner/users.json` with scrypt password hashes and a
`secret.key`, both mode 0600. Keep these outside Git and protect backups.

```sh
python tools/ansible_runner/manage_users.py set alice --role operator
python tools/ansible_runner/manage_users.py set bob --role viewer
python tools/ansible_runner/manage_users.py disable bob
```

`set` also resets a password or changes a role; password changes and disabling
revoke access on the next request. Role changes also apply on the next request.
There must always be at least one enabled administrator. Run account management
serially, not concurrently. Restart the runner after initial setup.

## Roles

| Role | Permissions |
| --- | --- |
| Viewer | Dashboard, workflows list, inventory paths, environment status, shared saved suites, job history and logs |
| Operator | Viewer plus input browsing/reading, validation, controller lookups, run suites/plays, create/edit/delete their own saved suites, cancel shared jobs and delete their own finished runs |
| Admin | Operator plus save input files, fetch/refresh Git repositories, create/install execution environments, manage/reorder all saved suites and delete any finished run |

Permissions are enforced server-side for every route, not just buttons.
Unknown endpoints are denied. Sessions expire after eight hours; sign-out revokes
the session. Restarting the single runner process signs everyone out. Login is
limited to ten attempts per source IP per five minutes. Behind a proxy, source
IPs may be shared; forwarded identity/IP headers are deliberately not trusted.

## Configuration and operation

- `RUNNER_AUTH_DIR`: account and signing-secret directory, default above.
- `RUNNER_USERS_FILE`: override the account JSON path.
- `RUNNER_SECRET_KEY`: optional signing secret, at least 32 characters; otherwise
  the application reads `RUNNER_AUTH_DIR/secret.key`. Keep it stable and private.
- Cookies default to Secure, HttpOnly and SameSite=Lax. Deploy behind HTTPS.
- Unsafe requests require the session CSRF token, including login and sign-out.
- For **localhost development only**, use `RUNNER_COOKIE_SECURE=false` on an HTTP
  server. Never use that setting on the shared server.

Example localhost launch after setup:

```sh
RUNNER_HOST=127.0.0.1 RUNNER_PORT=5015 RUNNER_COOKIE_SECURE=false \
  python tools/ansible_runner/app.py
```

Use a **single process** for this pilot: active process handles, cancellation, sessions and
login throttles are process-local. Multiple web workers are not supported yet.
Use a production WSGI server/reverse proxy and TLS for shared access; Flask's
development server is for local verification only.

All roles are trusted team members: history/logs can contain sensitive workflow
output, and Operators execute powerful Ansible workflows under the service
account. This is not tenant isolation or a sandbox for untrusted users. Restrict
OS permissions and network exposure. Basic credential/log redaction is
implemented, but cannot guarantee removal of every secret from arbitrary output.
Complete audit trails and SSO remain separate server-readiness work. Do not
publish the runner to the Internet on the strength of login alone.

Saved controller connections are shared team resources. Admins alone may save,
rotate or delete them; Operators may execute using any saved connection, while
Viewers may only view metadata. Profile endpoints never return passwords. The
Fernet-encrypted credential database and its separate encryption key live in the
protected account directory. Keep the key out of Git and protect its backups
separately. There are no per-profile user grants in this version.
