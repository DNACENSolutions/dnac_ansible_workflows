import json
import unittest
from unittest.mock import patch

import test_history

runner = test_history.runner


class RerunTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_history.PersistentHistoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.client = self.fixture.client
        self.original = self.fixture.add_job(status='failed', suite='original-suite')
        self.original.metadata.update(workflow='edge', playbook='cleanup.yml', vars_file='input.yml',
                                      inventory='hosts.yml', vars_source={'kind': 'git', 'id': 'repo_1'},
                                      inventory_source={'kind': 'git', 'id': 'repo_1'}, managed_venv=True,
                                      venv_path='.venv312', verbosity='-v',
                                      catalyst_connection_enabled=True,
                                      catalyst_connection_profile_id='profile-1',
                                      catalyst_connection_host='controller.test',
                                      catalyst_connection_username='operator', catalyst_connection_verify='true')
        runner._persist_job(self.original)

    def launch(self):
        return self.client.post('/api/jobs/abcdef01/rerun', headers=self.fixture.headers())

    def mock_builder(self, data, **kwargs):
        self.payload = data
        job = runner.Job('abcdef02', ['ansible-playbook'], '.', data['label'],
                         metadata={'submitted_by': data['_submitted_by']})
        return job, {}

    def test_launches_one_job_and_deduplicates_without_touching_siblings(self):
        sibling = self.fixture.add_job('abcdef03', suite='original-suite', index=2)
        self.fixture.restart()
        self.fixture.login('alice')
        with patch.object(runner, '_resolve_controller_reference', return_value={'enabled': True, 'password': 'SECRET'}), \
             patch.object(runner, '_build_run_job', side_effect=self.mock_builder) as build, \
             patch.object(runner.threading, 'Thread') as thread:
            response = self.launch()
            self.assertEqual(response.status_code, 202, response.text)
            self.assertEqual(self.payload['_submitted_by'], 'alice')
            self.assertEqual(self.payload['playbook'], 'cleanup.yml')
            self.assertEqual(self.payload['vars_source']['id'], 'repo_1')
            self.assertEqual(self.payload['venv_path'], '.venv312')
            self.assertNotIn('suite_launch_id', self.payload)
            self.assertEqual(runner._jobs['abcdef02'].metadata['rerun_of'], 'abcdef01')
            self.assertEqual(runner._jobs['abcdef03'].status, 'completed')
            again = self.launch()
            self.assertEqual(again.status_code, 200)
            self.assertTrue(again.get_json()['existing'])
            build.assert_called_once()
            thread.assert_called_once()
            thread.return_value.start.assert_called_once()
            self.assertNotIn('SECRET', response.text)
        self.fixture.restart()
        self.assertEqual(runner._jobs['abcdef02'].metadata['rerun_of'], 'abcdef01')

    def test_permissions_and_csrf(self):
        for user in ('bob', 'viewer'):
            self.fixture.login(user)
            with patch.object(runner, '_build_run_job') as build:
                self.assertEqual(self.launch().status_code, 403)
                build.assert_not_called()
        self.fixture.login('alice')
        self.assertEqual(self.client.post('/api/jobs/abcdef01/rerun').status_code, 403)

    def test_running_completed_and_active_suite_are_blocked(self):
        with patch.object(runner, '_build_run_job') as build:
            for status in ('running', 'completed', 'cancelled'):
                self.original.status = status
                self.assertNotEqual(self.launch().status_code, 202)
            self.original.status = 'failed'
            runner._active_suites.add('original-suite')
            self.assertEqual(self.launch().status_code, 403)
            build.assert_not_called()

    def test_unavailable_credentials_and_files_do_not_launch(self):
        with patch.object(runner, '_resolve_controller_reference', side_effect=ValueError('Saved controller no longer exists')), \
             patch.object(runner.threading, 'Thread') as thread:
            self.assertEqual(self.launch().status_code, 409)
            thread.assert_not_called()
        with patch.object(runner, '_resolve_controller_reference', return_value={}), \
             patch.object(runner, '_build_run_job', return_value=(None, 'Vars file not found')), \
             patch.object(runner.threading, 'Thread') as thread:
            self.assertEqual(self.launch().status_code, 409)
            thread.assert_not_called()

    def test_extra_arguments_remain_blocked_after_restart(self):
        self.original.metadata['extra_args'] = '-e password=DO_NOT_STORE'
        runner._persist_job(self.original)
        self.fixture.restart()
        with patch.object(runner, '_build_run_job') as build:
            response = self.launch()
            self.assertEqual(response.status_code, 409)
            self.assertIn('extra arguments', response.text)
            build.assert_not_called()
        self.assertNotIn(b'DO_NOT_STORE', (self.fixture.root / 'history/history.sqlite3').read_bytes())

    def test_legacy_history_requires_unique_saved_suite(self):
        self.original.metadata.pop('vars_source')
        run = {'workflow': 'edge', 'playbook': 'cleanup.yml', 'vars': 'input.yml', 'inventory': 'hosts.yml',
               'repo': 'repo_1', 'repo_details': {'source': {'kind': 'git', 'id': 'repo_1'}},
               'target_details': {'profile_id': 'profile-1'}}
        with runner._suite_database() as database:
            database.execute('INSERT INTO saved_suites VALUES(?,?,?,?,?)',
                             ('suite-1', 'alice', 1, 0, json.dumps({'name': 'Test suite', 'runs': [run]})))
        self.original.metadata['suite_name'] = 'Test suite'
        with patch.object(runner, '_resolve_controller_reference', return_value={}), \
             patch.object(runner, '_build_run_job', side_effect=self.mock_builder), \
             patch.object(runner.threading, 'Thread'):
            self.assertEqual(self.launch().status_code, 202)
        self.original.metadata.pop('rerun_job_id')
        with runner._suite_database() as database:
            database.execute('INSERT INTO saved_suites VALUES(?,?,?,?,?)',
                             ('suite-2', 'alice', 1, 1, json.dumps({'name': 'Test suite', 'runs': [run]})))
        self.assertEqual(self.launch().status_code, 409)


if __name__ == '__main__':
    unittest.main()
