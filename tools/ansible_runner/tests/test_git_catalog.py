import json
import shutil
import subprocess
import threading
import unittest
from unittest.mock import patch

import test_history

runner = test_history.runner


class GitCatalogTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_history.PersistentHistoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.client = self.fixture.client
        self.cache = self.fixture.root / 'cache'
        self.enterContext(patch.object(runner, 'GIT_REPOS_DIR', self.cache))
        self.enterContext(patch.object(runner, '_repo_fetch_locks', {}))
        self.clone = self.enterContext(patch.object(runner, '_clone_git_repo', side_effect=self.fake_clone))
        self.enterContext(patch.object(runner, '_run_git_head', return_value=subprocess.CompletedProcess([], 0, 'abc123\n')))

    def fake_clone(self, url, ref, target):
        (target / '.git').mkdir(parents=True)
        (target / 'data.yml').write_text('example: true\n')
        return subprocess.CompletedProcess([], 0, '')

    def fetch(self, **values):
        payload = dict(repo_url='https://github.com/example/inputs.git', ref='main')
        payload.update(values)
        return self.client.post('/api/git/fetch', json=payload,
                                headers=self.fixture.headers())

    def test_multiple_repositories_and_branches_are_independent(self):
        first = self.fetch().json['source']['id']
        branch = self.fetch(ref='demo').json['source']['id']
        other = self.fetch(repo_url='https://github.com/example/other.git').json['source']['id']
        self.assertEqual(len({first, branch, other}), 3)
        self.assertEqual(len(self.client.get('/api/git/repositories').json), 3)

    def test_shared_catalog_survives_logout_and_restart(self):
        result = self.fetch()
        self.assertEqual(result.status_code, 200, result.text)
        source = result.json['source']
        self.fixture.restart()
        for name in ('alice', 'viewer'):
            self.fixture.login(name)
            records = self.client.get('/api/git/repositories').json
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]['source'], source)
            self.assertTrue(records[0]['available'])

    def test_add_reuses_snapshot_and_explicit_refresh_keeps_old_snapshot(self):
        first = self.fetch().json
        second = self.fetch().json
        self.assertEqual(first['source']['id'], second['source']['id'])
        self.assertEqual(self.clone.call_count, 1)
        updated = self.fetch(refresh=True).json
        self.assertNotEqual(first['source']['id'], updated['source']['id'])
        self.assertIsNotNone(runner._resolve_git_source(first['source']))
        self.assertEqual(self.client.get('/api/git/repositories').json[0]['id'], updated['source']['id'])

    def test_remove_only_admin_and_preserves_cached_suite_inputs(self):
        source = self.fetch().json['source']
        path = '/api/git/repositories/' + source['id']
        for user in ('viewer', 'alice'):
            self.fixture.login(user)
            self.assertEqual(self.client.delete(path, headers=self.fixture.headers()).status_code, 403)
        self.fixture.login('admin')
        self.assertEqual(self.client.delete(path, headers=self.fixture.headers()).status_code, 200)
        self.assertEqual(self.client.get('/api/git/repositories').json, [])
        self.assertIsNotNone(runner._resolve_git_source(source))

    def test_missing_cache_visible_and_can_be_refetched(self):
        source = self.fetch().json['source']
        shutil.rmtree(runner._resolve_git_source(source))
        self.assertFalse(self.client.get('/api/git/repositories').json[0]['available'])
        self.assertEqual(self.fetch().status_code, 200)
        self.assertEqual(self.clone.call_count, 2)

    def test_duplicate_inflight_fetch_returns_conflict_without_second_clone(self):
        key = ('https://github.com/example/inputs.git', 'main')
        lock = threading.Lock()
        lock.acquire()
        runner._repo_fetch_locks[key] = lock
        try:
            self.assertEqual(self.fetch().status_code, 409)
            self.clone.assert_not_called()
        finally:
            lock.release()

    def test_failed_refresh_preserves_registered_snapshot(self):
        source = self.fetch().json['source']
        self.clone.side_effect = None
        self.clone.return_value = subprocess.CompletedProcess([], 1, 'fixture failure')
        self.assertEqual(self.fetch(refresh=True).status_code, 500)
        self.assertEqual(self.client.get('/api/git/repositories').json[0]['source'], source)

    def test_credentials_in_urls_rejected_before_persistence(self):
        result = self.client.post('/api/git/fetch', json={'repo_url': 'https://user:TEST_SECRET@github.com/example/inputs.git'},
                                  headers=self.fixture.headers())
        self.assertEqual(result.status_code, 400)
        self.clone.assert_not_called()
        self.assertNotIn('TEST_SECRET', json.dumps(self.client.get('/api/git/repositories').json))


if __name__ == '__main__':
    unittest.main()
