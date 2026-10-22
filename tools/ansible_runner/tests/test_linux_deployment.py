import contextlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import Mock, patch

DEPLOY = Path(__file__).parents[1] / 'deploy'
spec = importlib.util.spec_from_file_location('runner_preflight', DEPLOY / 'preflight.py')
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class LinuxDeploymentTests(unittest.TestCase):
    def test_gunicorn_keeps_single_private_worker(self):
        config = runpy.run_path(str(DEPLOY / 'gunicorn.conf.py'))
        self.assertEqual(config['workers'], 1)
        self.assertEqual(config['bind'], '127.0.0.1:5005')
        self.assertEqual(config['worker_class'], 'gthread')
        self.assertGreaterEqual(config['threads'], 8)
        self.assertFalse(config['preload_app'])
        self.assertFalse(config['reload'])
        self.assertEqual(config['max_requests'], 0)
        self.assertTrue((Path(config['chdir']) / 'tools/ansible_runner/app.py').is_file())

    def test_service_uses_non_root_and_cleans_children(self):
        unit = (DEPLOY / 'catalystcenter-runner.service').read_text()
        self.assertIn('User=catalyst-runner', unit)
        self.assertIn('KillMode=control-group', unit)
        self.assertIn('UMask=0077', unit)
        self.assertIn('ExecStartPre=', unit)
        self.assertIn('StateDirectoryMode=0700', unit)
        self.assertNotIn('8600', unit)
        self.assertNotIn('0.0.0.0', unit)

    def test_directory_check_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / 'not-created' / 'history'
            self.assertTrue(preflight.directory_ready(candidate))
            self.assertFalse(candidate.parent.exists())

    def test_private_files_reject_group_and_world_access(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'secret'
            path.write_text('test-only')
            path.chmod(0o600)
            self.assertTrue(preflight.private_path(path))
            path.chmod(0o640)
            self.assertFalse(preflight.private_path(path))

    def run_checks(self, linux=True, occupied=False, root=False, import_ok=True):
        def command(args, **kwargs):
            if 'collection' in args:
                return Mock(returncode=0, stdout=json.dumps({'collections': {'cisco.catalystcenter': {}}}))
            return Mock(returncode=0 if import_ok else 1)

        with tempfile.TemporaryDirectory() as directory:
            auth = Path(directory)
            project = auth / 'project'
            (project / 'workflows').mkdir(parents=True)
            users = auth / 'users.json'
            users.write_text(json.dumps({'admin': {'role': 'admin', 'password_hash': 'scrypt:test'}}))
            users.chmod(0o600)
            secret = auth / 'secret.key'
            secret.write_text('x' * 48)
            secret.chmod(0o600)
            environment = {'RUNNER_AUTH_DIR': str(auth), 'RUNNER_USERS_FILE': str(users),
                           'RUNNER_HISTORY_DIR': str(auth / 'history'), 'RUNNER_COOKIE_SECURE': 'true',
                           'ANSIBLE_LOCAL_TEMP': str(auth / 'local'), 'ANSIBLE_REMOTE_TEMP': str(auth / 'remote')}
            output = io.StringIO()
            with patch.dict(preflight.os.environ, environment), \
                 patch.object(preflight, 'ROOT', project), \
                 patch.object(preflight.platform, 'system', return_value='Linux' if linux else 'Darwin'), \
                 patch.object(preflight.os, 'geteuid', return_value=0 if root else auth.stat().st_uid), \
                 patch.object(preflight.shutil, 'which', return_value='/usr/bin/git'), \
                 patch.object(preflight.subprocess, 'run', side_effect=command), \
                 patch.object(preflight, 'check_port', return_value=not occupied), \
                 contextlib.redirect_stdout(output):
                code = preflight.main([])
            return code, output.getvalue()

    def test_preflight_success(self):
        code, output = self.run_checks()
        self.assertEqual(code, 0, output)
        self.assertNotIn('scrypt:test', output)

    def test_preflight_rejects_wrong_os_root_occupied_port_and_broken_import(self):
        for kwargs in ({'linux': False}, {'root': True}, {'occupied': True}, {'import_ok': False}):
            with self.subTest(kwargs=kwargs):
                code, _ = self.run_checks(**kwargs)
                self.assertEqual(code, 1)


if __name__ == '__main__':
    unittest.main()
