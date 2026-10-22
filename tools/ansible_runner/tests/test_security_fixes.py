import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml
from jinja2 import Environment
import test_history

runner = test_history.runner


class SecurityFixTests(unittest.TestCase):
    def test_catc_destination_must_come_from_server_allowlist(self):
        with patch.dict(os.environ, {'RUNNER_CATC_ALLOWED_HOSTS': 'catc.example.test,10.195.243.100', 'HOSTIP': ''}):
            self.assertEqual(runner._catc_base_url({'host': 'catc.example.test'}), 'https://catc.example.test')
            for host in ('127.0.0.1', '169.254.169.254', 'catc.example.test@evil.test',
                         'catc.example.test/other', 'evil.test', 'catc.example.test:443'):
                with self.subTest(host=host), self.assertRaises(ValueError):
                    runner._catc_base_url({'host': host})
        with patch.dict(os.environ, {'RUNNER_CATC_ALLOWED_HOSTS': '', 'HOSTIP': ''}):
            with self.assertRaises(ValueError):
                runner._catc_base_url({'host': 'catc.example.test'})

    def test_catc_redirects_and_invalid_paths_are_blocked(self):
        with self.assertRaises(runner.urllib.error.URLError):
            runner._NoCatcRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.test')
        with self.assertRaises(ValueError), patch.object(runner, '_catc_open') as opened:
            runner._catc_get('//evil.test/path', catalyst_connection={'host': 'catc.example.test'})
        opened.assert_not_called()

    def test_confined_paths_block_escape_and_symlinks(self):
        root = self.fixture.root / 'allowed'
        root.mkdir()
        outside = self.fixture.root / 'outside'
        outside.mkdir()
        (root / 'escape').symlink_to(outside, target_is_directory=True)
        for value in ('../outside', str(outside), 'escape', '\x00bad'):
            with self.subTest(value=value):
                self.assertIsNone(runner._confined_path(value, (root,), root))
        self.assertEqual(runner._confined_path('valid.yml', (root,), root), root.resolve() / 'valid.yml')

    def setUp(self):
        self.fixture = test_history.PersistentHistoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.client = self.fixture.client

    def test_viewer_cannot_read_password_from_command_or_metadata(self):
        job = self.fixture.add_job()
        job.metadata['extra_args'] = '-e password=DO_NOT_STORE'
        self.fixture.login('viewer')
        for path in ('/api/jobs', '/api/jobs/abcdef01'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('DO_NOT_STORE', response.text)
            self.assertNotIn('extra_args', response.text)

    def test_log_redaction_before_disk_api_raw_download_and_stream(self):
        job = self.fixture.add_job()
        job.secret_values.add('fixture-credential')
        job.put('A standalone credential: fixture-credential\n')
        job.put('password="another-fixture-value"\n')
        job.put('Authorization: Bearer sample-token\n')
        job.put('https://user:example-password@example.invalid/path\n')
        job.put('-----BEGIN PRIVATE KEY-----\n')
        job.put('private-key-body\n')
        job.put('-----END PRIVATE KEY-----\n')
        runner._persist_job(job)
        self.fixture.login('viewer')
        for path in ('/api/jobs/abcdef01', '/api/jobs/abcdef01/log', '/api/run/abcdef01/stream'):
            response = self.client.get(path)
            for value in ('fixture-credential', 'another-fixture-value', 'sample-token', 'example-password', 'private-key-body'):
                self.assertNotIn(value, response.text)
        stored = (self.fixture.root / 'history/logs/abcdef01.jsonl').read_text()
        self.assertNotIn('fixture-credential', stored)
        self.assertNotIn('private-key-body', stored)

    def test_capture_yaml_and_extra_variable_credentials(self):
        inputs = self.fixture.root / 'vars.yml'
        inputs.write_text('nested:\n  enable_password: yaml-fixture\n')
        job = runner.Job('abcdef02', ['ansible-playbook', '-e', 'vault_password=cli-fixture'], '.',
                         env_overrides={'CATALYST_CENTER_PASSWORD': 'env-fixture'})
        job.capture_input_secrets([inputs])
        for secret in ('yaml-fixture', 'cli-fixture', 'env-fixture'):
            self.assertEqual(job.redact_output(secret), '[REDACTED]')

    def test_legacy_logs_are_scrubbed_on_recovery(self):
        self.fixture.add_job()
        log = self.fixture.root / 'history/logs/abcdef01.jsonl'
        log.write_text(json.dumps('password="legacy-fixture"\n') + '\n')
        self.fixture.restart()
        self.assertNotIn('legacy-fixture', log.read_text())
        self.assertNotIn('legacy-fixture', self.client.get('/api/jobs/abcdef01/log').text)

    def test_cancel_during_job_build_never_executes_replacement(self):
        for fails in (False, True):
            with self.subTest(build_fails=fails):
                old = runner.Job('abcdef03', [], '.', metadata={'suite_launch_id': 'cancel-race'})
                runner._jobs[old.id] = old
                data = {'_reserved_job_id': old.id, 'suite_launch_id': 'cancel-race'}

                def build(*args, **kwargs):
                    runner._cancel_job(old)
                    if fails:
                        return None, 'simulated preparation failure'
                    return runner.Job(old.id, [], '.', metadata={'suite_launch_id': 'cancel-race'}), {}

                with patch.object(runner, '_build_run_job', side_effect=build), patch.object(runner, '_exec') as execute:
                    runner._exec_suite_sequence([data], 'stop')
                execute.assert_not_called()
                self.assertIs(runner._jobs[old.id], old)
                self.assertEqual(old.status, 'cancelled')

    def test_prepared_job_keeps_registered_identity_for_inflight_cancel(self):
        old = runner.Job('abcdef04', [], '.')
        runner._jobs[old.id] = old
        prepared = runner.Job(old.id, ['ansible-playbook'], '.')
        self.assertIs(runner._install_suite_job(prepared), old)
        runner._cancel_job(old)
        with patch.object(runner.subprocess, 'Popen') as process:
            runner._exec(old)
        process.assert_not_called()

    def test_failed_log_delete_retains_job_and_can_retry(self):
        self.fixture.add_job()
        with patch.object(Path, 'unlink', side_effect=PermissionError('simulated log permissions')):
            response = self.client.delete('/api/jobs/abcdef01', headers=self.fixture.headers())
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.client.get('/api/jobs/abcdef01').status_code, 200)
        self.assertTrue((self.fixture.root / 'history/logs/abcdef01.jsonl').exists())
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.fixture.headers()).status_code, 200)
        self.fixture.restart()
        self.assertEqual(self.client.get('/api/jobs/abcdef01').status_code, 404)

    def test_pending_suite_delete_recovers_after_partial_file_cleanup(self):
        self.fixture.add_job(suite='pending-suite')
        self.fixture.add_job('abcdef02', suite='pending-suite', index=2)
        unlink = Path.unlink

        def fail_second(path, **kwargs):
            if path.name == 'abcdef02.jsonl':
                raise PermissionError('simulated second log permissions')
            return unlink(path, **kwargs)

        with patch.object(Path, 'unlink', fail_second):
            response = self.client.delete('/api/suites/pending-suite', headers=self.fixture.headers())
        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(runner._jobs), 2)
        self.fixture.restart()
        self.assertEqual(self.client.get('/api/jobs').get_json(), [])
        self.assertFalse((self.fixture.root / 'history/logs/abcdef02.jsonl').exists())

    def test_readiness_is_opt_in_for_existing_non_ip_queries(self):
        path = Path(runner.__file__).parents[2] / 'workflows/network_devices_info/playbook/network_devices_info_playbook.yml'
        tasks = yaml.safe_load(path.read_text())[0]['tasks']
        readiness = [task for task in tasks if task.get('name') in {
            'Collect device IPs for inventory readiness checks', 'Require explicit device IPs for inventory readiness checks',
            'Authenticate for inventory readiness checks', 'Check inventory readiness before gathering device information'}]
        self.assertEqual(len(readiness), 4)
        environment = Environment()
        environment.filters['bool'] = bool
        for selector in ({'hostname': ['switch']}, {'serial_number': ['serial']}, {'site_hierarchy': 'Global/Lab'}):
            for task in readiness:
                if task['name'] == 'Collect device IPs for inventory readiness checks':
                    self.assertNotIn('when', task)
                elif task['name'] == 'Require explicit device IPs for inventory readiness checks':
                    expression = environment.compile_expression(task['when'])
                    self.assertFalse(expression())
                    self.assertTrue(expression(network_devices_info_wait_for_readiness=True))
                else:
                    expressions = [environment.compile_expression(value) for value in task['when']]
                    self.assertFalse(all(expression(readiness_ips=[]) for expression in expressions))
                    self.assertTrue(all(expression(readiness_ips=['192.0.2.1']) for expression in expressions))

    def test_retry_references_survive_restart_without_source_secrets(self):
        job = self.fixture.add_job(status='failed')
        job.metadata.update(workflow='provision', playbook='play.yml', vars_file='vars.yml',
                            vars_source={'kind': 'git', 'id': 'repo_123', 'password': 'DO_NOT_STORE'},
                            inventory_source={'kind': 'git', 'id': 'repo_123'},
                            catalyst_connection_profile_id='profile-1',
                            catalyst_connection_host='controller.test',
                            catalyst_connection_username='operator',
                            catalyst_connection_verify='true',
                            catalyst_connection_password='DO_NOT_STORE')
        runner._persist_job(job)
        self.fixture.restart()
        data = self.client.get('/api/jobs/abcdef01').get_json()
        self.assertEqual(data['metadata']['vars_source'], {'kind': 'git', 'id': 'repo_123'})
        self.assertEqual(data['metadata']['catalyst_connection_profile_id'], 'profile-1')
        self.assertTrue(data['can_delete'])
        self.assertNotIn('DO_NOT_STORE', json.dumps(data))
        self.assertNotIn(b'DO_NOT_STORE', (self.fixture.root / 'history/history.sqlite3').read_bytes())


if __name__ == '__main__':
    unittest.main()
