import json
import unittest
from unittest.mock import patch
import test_history

runner = test_history.runner


class SharedSuitesTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_history.PersistentHistoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.client = self.fixture.client

    def send(self, method, path='/api/saved-suites', payload=None):
        return getattr(self.client, method)(path, json=payload, headers=self.fixture.headers())

    def create(self, **extra):
        payload = {'name': 'Shared demo', 'runs': [{'name': 'Read inventory', 'workflow': 'inventory',
                    'playbook': 'inventory.yml', 'vars': 'data.yml', 'repo': 'local',
                    'target_details': {'name': 'Lab', 'host': '192.0.2.1', 'username': 'test-user',
                                       'verify': 'true', 'password': 'MUST_NOT_STORE'}}], **extra}
        response = self.send('post', payload=payload)
        self.assertIn(response.status_code, (200, 201), response.get_json())
        return response.get_json()

    def test_shared_visibility_survives_restart_and_secrets_removed(self):
        suite = self.create(owner='spoof', password='MUST_NOT_STORE', metadata={'secret': 'MUST_NOT_STORE'})
        self.assertEqual(suite['owner'], 'admin')
        self.assertNotIn('password', suite['runs'][0]['target_details'])
        self.fixture.restart()
        self.fixture.login('viewer')
        result = self.client.get('/api/saved-suites').get_json()
        self.assertEqual(result[0]['id'], suite['id'])
        self.assertFalse(result[0]['can_edit'])
        self.assertNotIn('MUST_NOT_STORE', json.dumps(result))
        self.assertNotIn(b'MUST_NOT_STORE', (self.fixture.root / 'history/history.sqlite3').read_bytes())

    def test_viewer_cannot_write_and_operator_cannot_change_another_owners_suite(self):
        suite = self.create()
        path = '/api/saved-suites/' + suite['id']
        self.fixture.login('viewer')
        self.assertEqual(self.send('post', payload=suite).status_code, 403)
        self.assertEqual(self.send('put', path, suite).status_code, 403)
        self.assertEqual(self.send('delete', path, suite).status_code, 403)
        self.fixture.login('alice')
        self.assertEqual(self.send('put', path, suite).status_code, 403)
        self.assertEqual(self.send('delete', path, suite).status_code, 403)
        owned = self.create()
        self.assertEqual(owned['owner'], 'alice')
        self.assertTrue(owned['can_edit'])

    def test_update_conflicts_and_owner_is_immutable(self):
        self.fixture.login('alice')
        suite = self.create()
        path = '/api/saved-suites/' + suite['id']
        update = {**suite, 'name': 'Renamed', 'owner': 'admin'}
        response = self.send('put', path, update)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['owner'], 'alice')
        self.assertEqual(self.send('put', path, update).status_code, 409)
        self.assertEqual(self.send('delete', path, suite).status_code, 409)
        self.fixture.login('admin')
        self.assertEqual(self.send('delete', path, response.get_json()).status_code, 200)

    def test_delete_definition_keeps_job_history(self):
        self.fixture.add_job()
        suite = self.create()
        self.assertEqual(self.send('delete', '/api/saved-suites/' + suite['id'], suite).status_code, 200)
        self.fixture.restart()
        self.assertEqual(self.client.get('/api/saved-suites').get_json(), [])
        self.assertEqual(self.client.get('/api/jobs/abcdef01').status_code, 200)

    def test_browser_import_is_idempotent_without_overwriting_shared_changes(self):
        first = self.create(legacy_id='browser-id')
        second = self.create(legacy_id='browser-id', name='Changed import')
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(second['name'], first['name'])
        self.fixture.login('alice')
        own = self.create(legacy_id='browser-id')
        self.assertNotEqual(own['id'], first['id'])

    def test_order_is_admin_only_and_detects_stale_lists(self):
        first, second = self.create(), self.create()
        payload = {'items': [{'id': second['id'], 'revision': 1}, {'id': first['id'], 'revision': 1}]}
        self.fixture.login('alice')
        self.assertEqual(self.send('post', '/api/saved-suites/order', payload).status_code, 403)
        self.fixture.login('admin')
        self.assertEqual(self.send('post', '/api/saved-suites/order', payload).status_code, 200)
        rows = self.client.get('/api/saved-suites').get_json()
        self.assertEqual([row['id'] for row in rows], [second['id'], first['id']])
        self.assertEqual(self.send('post', '/api/saved-suites/order', payload).status_code, 409)

    def test_schema_errors_csrf_and_credential_urls(self):
        for payload in ([], {}, {'name': 'bad', 'runs': []}, {'name': 'bad', 'runs': ['bad']},
                        {'name': 'bad', 'runs': [{'repo_details': {'source': {'repo_url': 'https://user:secret@example.com/repo'}}}]}):
            self.assertEqual(self.send('post', payload=payload).status_code, 400)
        self.assertEqual(self.client.post('/api/saved-suites', json={}).status_code, 403)

    def test_missing_repo_catalog_and_viewer_restriction(self):
        with patch.object(runner, '_resolve_git_source', return_value=None):
            self.assertEqual(self.client.get('/api/git/catalog?source_id=missing').status_code, 404)
        self.fixture.login('viewer')
        self.assertEqual(self.client.get('/api/git/catalog?source_id=missing').status_code, 403)


if __name__ == '__main__':
    unittest.main()
