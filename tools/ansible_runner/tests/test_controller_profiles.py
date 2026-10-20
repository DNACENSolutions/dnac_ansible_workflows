import json
import os
import stat
import unittest
from unittest.mock import patch

import test_history

runner = test_history.runner


class ControllerProfilesTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_history.PersistentHistoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.client = self.fixture.client
        self.value = dict(name='Lab A', host='catc-a.example.test', username='demo',
                          password='fixture-secret-do-not-expose', verify='true')

    def save(self, value=None):
        response = self.client.post('/api/controller-profiles', json=value or self.value,
                                    headers=self.fixture.headers())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn(self.value['password'], response.text)
        return response.json

    def test_encrypted_storage_permissions_and_reload(self):
        saved = self.save()
        root = self.fixture.root
        self.assertNotIn(self.value['password'].encode(), (root / 'controllers.sqlite3').read_bytes())
        for name in ('controllers.sqlite3', 'controllers.key'):
            self.assertEqual(stat.S_IMODE((root / name).stat().st_mode), 0o600)
        self.fixture.login('alice')
        self.assertEqual(self.client.get('/api/controller-profiles').json, [saved])
        resolved = runner._resolve_controller_reference({'profile_id': saved['profile_id']})
        self.assertEqual(resolved['password'], self.value['password'])
        self.assertEqual(resolved['host'], self.value['host'])

    def test_multiple_controllers_resolve_independently(self):
        first = self.save()
        second = self.save(dict(self.value, name='Lab B', host='catc-b.example.test', password='other-fixture'))
        for saved, password in ((first, self.value['password']), (second, 'other-fixture')):
            self.assertEqual(runner._resolve_controller_reference({'profile_id': saved['profile_id']})['password'], password)
        with patch.dict(os.environ, HOSTIP='', RUNNER_CATC_ALLOWED_HOSTS=''):
            self.assertEqual(runner._catc_base_url({'host': second['host']}), 'https://' + second['host'])
            with self.assertRaises(ValueError):
                runner._catc_base_url({'host': 'unapproved.example.test'})

    def test_only_admin_can_manage_profiles_and_csrf_is_required(self):
        saved = self.save()
        self.assertEqual(self.client.post('/api/controller-profiles', json=self.value).status_code, 403)
        for name in ('alice', 'viewer'):
            self.fixture.login(name)
            self.assertEqual(self.client.post('/api/controller-profiles', json=self.value,
                                             headers=self.fixture.headers()).status_code, 403)
            self.assertEqual(self.client.delete('/api/controller-profiles/' + saved['profile_id'],
                                               headers=self.fixture.headers()).status_code, 403)
            self.assertNotIn(self.value['password'], self.client.get('/api/controller-profiles').text)

    def test_updates_preserve_or_rotate_password_and_reject_changed_identity(self):
        saved = self.save()
        self.save(dict(saved, password=''))
        self.assertEqual(runner._resolve_controller_reference(saved)['password'], self.value['password'])
        self.save(dict(saved, password='rotated-fixture'))
        self.assertEqual(runner._resolve_controller_reference(saved)['password'], 'rotated-fixture')
        response = self.client.post('/api/controller-profiles', json=dict(saved, host='other.example.test'),
                                    headers=self.fixture.headers())
        self.assertEqual(response.status_code, 400)
        for value in (dict(saved, host='forged.example.test'), dict(saved, password='unsaved-edit')):
            with self.assertRaises(ValueError):
                runner._resolve_controller_reference(value)

    def test_suite_dispatch_resolves_before_background_thread(self):
        saved = self.save()
        self.fixture.login('alice')
        with patch.object(runner, '_stamp_runs') as stamp, patch.object(runner.threading, 'Thread'):
            response = self.client.post('/api/run/suites', json={'suites': [{'runs': [
                {'catalyst_connection': dict(saved, enabled=True)}]}]}, headers=self.fixture.headers())
        self.assertEqual(response.status_code, 200)
        connection = stamp.call_args.args[0][0]['catalyst_connection']
        self.assertEqual(connection['password'], self.value['password'])
        self.assertNotIn(self.value['password'], response.text)

    def test_deleted_profile_fails_before_dispatch(self):
        saved = self.save()
        self.client.delete('/api/controller-profiles/' + saved['profile_id'], headers=self.fixture.headers())
        with patch.object(runner, '_build_run_job') as build:
            response = self.client.post('/api/run', json={'catalyst_connection': saved}, headers=self.fixture.headers())
        self.assertEqual(response.status_code, 400)
        build.assert_not_called()

    def test_suite_keeps_reference_not_password(self):
        saved = self.save()
        cleaned = runner._clean_saved_suite({'name': 'Demo', 'runs': [{'target_details': dict(saved, password=self.value['password'])}]})
        self.assertEqual(cleaned['runs'][0]['target_details']['profile_id'], saved['profile_id'])
        self.assertNotIn(self.value['password'], json.dumps(cleaned))

    def test_missing_key_fails_closed_without_replacement(self):
        saved = self.save()
        key = self.fixture.root / 'controllers.key'
        key.unlink()
        self.assertEqual(self.client.get('/api/controller-profiles').status_code, 503)
        self.assertFalse(key.exists())
        with self.assertRaises(ValueError):
            runner._resolve_controller_reference(saved)


if __name__ == '__main__':
    unittest.main()
