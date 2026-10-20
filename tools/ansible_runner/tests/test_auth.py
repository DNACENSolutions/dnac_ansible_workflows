import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from werkzeug.security import generate_password_hash

spec = importlib.util.spec_from_file_location('auth_runner', Path(__file__).parents[1] / 'app.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.directory = self.enterContext(tempfile.TemporaryDirectory())
        self.path = Path(self.directory) / 'users.json'
        self.users = {role: {'role': role, 'enabled': True,
                            'password_hash': generate_password_hash('test-password-123')}
                      for role in ('viewer', 'operator', 'admin')}
        self.save()
        self.enterContext(patch.dict(runner.app.config, TESTING=True, SECRET_KEY='x' * 48,
                                    RUNNER_USERS_FILE=str(self.path), SESSION_COOKIE_SECURE=False))
        self.enterContext(patch.object(runner, '_auth_sessions', {}))
        self.enterContext(patch.object(runner, '_auth_attempts', {}))
        self.client = runner.app.test_client()

    def save(self):
        self.path.write_text(json.dumps(self.users))

    def login(self, role='viewer'):
        self.client.get('/login')
        with self.client.session_transaction() as session:
            csrf = session['csrf']
        return self.client.post('/login', data={'username': role, 'password': 'test-password-123', 'csrf': csrf})

    def headers(self):
        with self.client.session_transaction() as session:
            return {'X-CSRF-Token': session['csrf']}

    def test_missing_config_fails_closed(self):
        self.path.unlink()
        self.assertEqual(self.client.get('/').status_code, 503)
        self.assertEqual(self.client.get('/api/jobs').status_code, 503)

    def test_login_and_setup_use_dashboard_branding(self):
        for setup in (False, True):
            if setup:
                self.path.unlink()
            response = self.client.get('/login')
            self.assertIn('<header>Cisco Validated Playbook Dashboard</header>', response.text)
            self.assertIn('<title>Sign In | Cisco Validated Playbook Dashboard</title>', response.text)
            self.assertNotIn('Cisco Catalyst Center Workflow Runner', response.text)

    def test_unauthenticated_gets_no_jobs_or_logs(self):
        for path in ('/api/jobs', '/api/file?path=a.yml', '/api/run/a/stream', '/api/jobs/a/log'):
            self.assertEqual(self.client.get(path).status_code, 401)
        self.assertEqual(self.client.get('/').status_code, 302)

    def test_login_logout_and_csrf(self):
        self.assertEqual(self.login().status_code, 302)
        self.assertEqual(self.client.get('/api/jobs').status_code, 200)
        self.assertEqual(self.client.post('/logout').status_code, 403)
        self.assertEqual(self.client.post('/logout', headers=self.headers()).status_code, 302)
        self.assertEqual(self.client.get('/api/jobs').status_code, 401)

    def test_favicon_request_does_not_invalidate_login_form(self):
        self.client.get('/login')
        with self.client.session_transaction() as session:
            token = session['csrf']
        self.client.get('/favicon.ico')
        response = self.client.post('/login', data={'username': 'viewer',
                                    'password': 'test-password-123', 'csrf': token})
        self.assertEqual(response.status_code, 302)

    def test_login_after_restart_and_favicon_uses_fresh_token(self):
        self.login()
        runner._auth_sessions.clear()
        self.test_favicon_request_does_not_invalidate_login_form()

    def test_viewer_cannot_execute_or_change_files(self):
        self.login()
        for path in ('/api/run', '/api/run/a/cancel', '/api/environment/setup', '/api/git/fetch'):
            self.assertEqual(self.client.post(path, json={}, headers=self.headers()).status_code, 403)
        self.assertEqual(self.client.put('/api/file', json={}, headers=self.headers()).status_code, 403)

    def test_operator_cannot_administer(self):
        self.login('operator')
        for path in ('/api/environment/create', '/api/environment/setup', '/api/git/fetch'):
            self.assertEqual(self.client.post(path, json={}, headers=self.headers()).status_code, 403)
        self.assertEqual(self.client.put('/api/file', json={}, headers=self.headers()).status_code, 403)
        self.assertNotEqual(self.client.post('/api/run/a/cancel', headers=self.headers()).status_code, 403)

    def test_account_revocation_and_role_changes_are_immediate(self):
        self.login('admin')
        self.users['admin']['role'] = 'viewer'
        self.save()
        self.assertEqual(self.client.post('/api/environment/setup', headers=self.headers()).status_code, 403)
        self.users['admin']['enabled'] = False
        self.save()
        self.assertEqual(self.client.get('/api/jobs').status_code, 401)

    def test_password_change_revokes_session(self):
        self.login()
        self.users['viewer']['password_hash'] = generate_password_hash('replacement-password')
        self.save()
        self.assertEqual(self.client.get('/api/jobs').status_code, 401)

    def test_expiry_and_restart_revoke_sessions(self):
        self.login()
        with self.client.session_transaction() as session:
            sid = session['sid']
        username, version, _ = runner._auth_sessions[sid]
        runner._auth_sessions[sid] = (username, version, 0)
        self.assertEqual(self.client.get('/api/jobs').status_code, 401)
        self.login()
        runner._auth_sessions.clear()
        self.assertEqual(self.client.get('/api/jobs').status_code, 401)

    def test_secure_cookie_and_rendered_role(self):
        with patch.dict(runner.app.config, SESSION_COOKIE_SECURE=True):
            response = self.client.get('/login')
            cookie = response.headers['Set-Cookie']
            for flag in ('Secure', 'HttpOnly', 'SameSite=Lax'):
                self.assertIn(flag, cookie)
        self.login('operator')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'operator', response.data)
        self.assertIn(b'Sign Out', response.data)

    def test_unknown_api_denied_and_all_existing_routes_classified(self):
        public = {'static', 'login', 'logout'}
        classified = runner._read_endpoints | runner._operator_endpoints | runner._admin_endpoints | public
        self.assertFalse({rule.endpoint for rule in runner.app.url_map.iter_rules()} - classified)
        self.login('admin')
        self.assertEqual(self.client.get('/api/unknown').status_code, 403)

    def test_headers_and_login_rate_limit(self):
        response = self.client.get('/login')
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')
        for _ in range(10):
            with self.client.session_transaction() as session:
                csrf = session['csrf']
            response = self.client.post('/login', data={'username': 'viewer', 'password': 'bad', 'csrf': csrf})
            self.assertEqual(response.status_code, 401)
        self.assertEqual(self.client.post('/login', data={'csrf': csrf}).status_code, 429)


if __name__ == '__main__':
    unittest.main()
