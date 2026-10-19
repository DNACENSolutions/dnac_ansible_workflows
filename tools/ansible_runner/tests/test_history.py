import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
import unittest
from unittest.mock import Mock, patch

from werkzeug.security import generate_password_hash

spec = importlib.util.spec_from_file_location('history_runner', Path(__file__).parents[1] / 'app.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class PersistentHistoryTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        users = self.root / 'users.json'
        password_hash = generate_password_hash('test-password-123')
        users.write_text(json.dumps({name: {'role': role, 'password_hash': password_hash}
                                     for name, role in [('admin', 'admin'), ('alice', 'operator'),
                                                        ('bob', 'operator'), ('viewer', 'viewer')]}))
        self.enterContext(patch.dict(runner.app.config, TESTING=True, SECRET_KEY='x' * 48,
                                    RUNNER_USERS_FILE=str(users), SESSION_COOKIE_SECURE=False,
                                    RUNNER_TEST_HISTORY=True, RUNNER_HISTORY_DIR=str(self.root / 'history')))
        for name, value in [('_history_ready', None), ('_jobs', {}), ('_auth_sessions', {}),
                            ('_auth_attempts', {}), ('_active_suites', set()), ('_cancelled_suites', set())]:
            self.enterContext(patch.object(runner, name, value))
        self.client = runner.app.test_client()
        self.login('admin')

    def login(self, username):
        self.client.get('/login')
        with self.client.session_transaction() as session:
            token = session['csrf']
        response = self.client.post('/login', data={'username': username,
                                    'password': 'test-password-123', 'csrf': token})
        self.assertEqual(response.status_code, 302)

    def headers(self):
        with self.client.session_transaction() as session:
            return {'X-CSRF-Token': session['csrf']}

    def add_job(self, jid='abcdef01', owner='alice', status='completed', suite=None, index=1):
        metadata = {'submitted_by': owner}
        if suite:
            metadata.update(suite_launch_id=suite, suite_run_index=index, suite_run_total=2,
                            suite_finished=True, suite_plan=[{'index': 1}, {'index': 2}])
        job = runner.Job(jid, ['ansible-playbook', '-e', 'password=DO_NOT_STORE'], '.', 'Test run', metadata=metadata)
        job.status, job.t0, job.t1 = status, 10, (None if status == 'running' else 20)
        runner._jobs[jid] = job
        job.put('hello\n')
        job.put('second chunk\nlast line\n')
        runner._persist_job(job)
        return job

    def restart(self):
        runner._jobs.clear()
        runner._history_ready = None
        self.assertEqual(self.client.get('/api/jobs').status_code, 200)

    def test_metadata_and_exact_log_survive_restart_without_credentials(self):
        self.add_job()
        self.restart()
        job = self.client.get('/api/jobs/abcdef01').get_json()
        self.assertEqual(job['status'], 'completed')
        self.assertEqual(job['metadata']['submitted_by'], 'alice')
        self.assertEqual(job['lines'], ['hello\n', 'second chunk\nlast line\n'])
        self.assertEqual(self.client.get('/api/jobs/abcdef01/log').text, 'hello\nsecond chunk\nlast line\n')
        self.assertNotIn(b'DO_NOT_STORE', (self.root / 'history/history.sqlite3').read_bytes())

    def test_restart_interrupts_running_and_queued_without_execution(self):
        self.add_job(status='running')
        self.add_job('abcdef02', status='queued')
        with patch.object(runner.subprocess, 'Popen') as process:
            self.restart()
        process.assert_not_called()
        self.assertTrue(all(job.status == 'interrupted' for job in runner._jobs.values()))
        self.restart()
        self.assertTrue(all(job.status == 'interrupted' for job in runner._jobs.values()))

    def test_completed_job_delete_removes_metadata_log_and_survives_restart(self):
        job = self.add_job()
        response = self.client.delete('/api/jobs/abcdef01', headers=self.headers())
        self.assertEqual(response.status_code, 200)
        self.assertFalse((self.root / 'history/logs/abcdef01.jsonl').exists())
        runner._persist_job(job)
        self.restart()
        self.assertEqual(self.client.get('/api/jobs/abcdef01').status_code, 404)
        self.assertEqual(self.client.get('/api/jobs/abcdef01/log').status_code, 404)

    def test_owner_admin_viewer_and_csrf_permissions(self):
        self.add_job()
        self.login('viewer')
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 403)
        self.login('bob')
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 403)
        self.login('alice')
        self.assertEqual(self.client.delete('/api/jobs/abcdef01').status_code, 403)
        self.assertTrue(self.client.get('/api/jobs').get_json()[0]['can_delete'])
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 200)

    def test_active_process_and_suite_cannot_be_deleted(self):
        job = self.add_job(status='running')
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 409)
        job.status, job.t1 = 'cancelled', 20
        job.proc = Mock()
        job.proc.poll.return_value = None
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 409)
        job.proc = None
        job.metadata['suite_launch_id'] = 'suite-a'
        runner._active_suites.add('suite-a')
        self.assertEqual(self.client.delete('/api/suites/suite-a', headers=self.headers()).status_code, 409)

    def test_suite_delete_is_all_or_nothing_for_ownership(self):
        self.add_job(suite='suite-a')
        self.add_job('abcdef02', owner='bob', suite='suite-a', index=2)
        self.login('alice')
        self.assertEqual(self.client.delete('/api/suites/suite-a', headers=self.headers()).status_code, 403)
        self.assertEqual(len(runner._jobs), 2)
        self.login('admin')
        self.assertEqual(self.client.delete('/api/suites/suite-a', headers=self.headers()).status_code, 200)
        self.restart()
        self.assertEqual(self.client.get('/api/jobs').get_json(), [])

    def test_child_delete_updates_remaining_suite_plan(self):
        self.add_job(suite='suite-a')
        self.add_job('abcdef02', suite='suite-a', index=2)
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 200)
        self.restart()
        metadata = runner._jobs['abcdef02'].metadata
        self.assertEqual(metadata['suite_run_total'], 1)
        self.assertEqual(metadata['suite_plan'], [{'index': 2}])

    def test_protected_storage_modes(self):
        self.add_job()
        for path, mode in [('history', 0o700), ('history/logs', 0o700),
                           ('history/history.sqlite3', 0o600), ('history/logs/abcdef01.jsonl', 0o600)]:
            self.assertEqual(stat.S_IMODE((self.root / path).stat().st_mode), mode)

    def test_live_orphan_after_restart_blocks_delete(self):
        job = self.add_job(status='running')
        job.proc = Mock(pid=os.getpid())
        runner._persist_job(job)
        self.restart()
        self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 409)
        with patch.object(runner, '_process_exists', return_value=False):
            self.assertEqual(self.client.delete('/api/jobs/abcdef01', headers=self.headers()).status_code, 200)

    def test_all_selected_suite_plays_are_durable_before_execution(self):
        runs = [{'label': 'First', '_submitted_by': 'spoof'}, {'label': 'Second'}]
        with patch.object(runner.threading, 'Thread'):
            response = self.client.post('/api/run/suite', json={'runs': runs}, headers=self.headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(runner._jobs), 2)
        self.assertTrue(all(job.metadata['submitted_by'] == 'admin' for job in runner._jobs.values()))
        self.restart()
        self.assertTrue(all(job.status == 'interrupted' for job in runner._jobs.values()))

    def test_execution_persists_terminal_state_and_log(self):
        job = self.add_job(status='queued')
        process = Mock(stdout=io.StringIO('execution output\n'), returncode=0)
        with patch.object(runner.subprocess, 'Popen', return_value=process):
            runner._exec(job)
        self.restart()
        self.assertEqual(runner._jobs[job.id].status, 'completed')
        self.assertIn('execution output\n', runner._jobs[job.id].lines)

    def test_unwritable_or_invalid_history_fails_closed(self):
        runner._history_ready = None
        with patch.object(runner, '_history_connection', side_effect=sqlite3.OperationalError('test unavailable')):
            self.assertEqual(self.client.get('/api/jobs').status_code, 503)

    def test_stop_policy_marks_remaining_registered_plays_not_run(self):
        with patch.object(runner.threading, 'Thread'):
            response = self.client.post('/api/run/suite', json={'runs': [{}, {}]}, headers=self.headers())
        suite = response.get_json()['suite_launch_id']
        jobs = list(runner._jobs.values())
        runs = [{'_reserved_job_id': job.id, 'suite_launch_id': suite, '_submitted_by': 'admin'} for job in jobs]
        with patch.object(runner, '_build_run_job', return_value=(None, 'invalid input')):
            runner._exec_suite_sequence(runs, 'stop')
        self.assertEqual(runner._jobs[jobs[0].id].status, 'failed')
        self.assertEqual(runner._jobs[jobs[1].id].status, 'not-run')
        self.assertNotIn(suite, runner._active_suites)


if __name__ == '__main__':
    unittest.main()
