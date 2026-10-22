import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from werkzeug.security import check_password_hash

spec = importlib.util.spec_from_file_location('manage_users', Path(__file__).parents[1] / 'manage_users.py')
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class AccountSetupTests(unittest.TestCase):
    def test_five_character_password_is_accepted_and_can_be_reset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.dict(os.environ, RUNNER_AUTH_DIR=str(root), RUNNER_USERS_FILE=str(root / 'users.json')):
                for command in (['init', 'admin'], ['set', 'admin', '--role', 'admin']):
                    with patch('sys.argv', ['manage_users.py'] + command), \
                         patch.object(manager.getpass, 'getpass', return_value='admin'), \
                         patch('builtins.print'):
                        manager.main()
                    user = json.loads((root / 'users.json').read_text())['admin']
                    self.assertTrue(check_password_hash(user['password_hash'], 'admin'))
                    self.assertEqual(user['role'], 'admin')

    def test_short_or_mismatched_password_is_rejected(self):
        for answers in (['abcd'], ['admin', 'other']):
            with self.subTest(answers=answers), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with patch.dict(os.environ, RUNNER_AUTH_DIR=str(root), RUNNER_USERS_FILE=str(root / 'users.json')), \
                     patch('sys.argv', ['manage_users.py', 'init', 'admin']), \
                     patch.object(manager.getpass, 'getpass', side_effect=answers), \
                     patch('sys.stderr'), self.assertRaises(SystemExit):
                    manager.main()
                self.assertFalse((root / 'users.json').exists())

    def test_init_creates_protected_secret_and_hashed_admin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'auth'
            with patch.dict(os.environ, RUNNER_AUTH_DIR=str(root), RUNNER_USERS_FILE=str(root / 'users.json')):
                with patch('sys.argv', ['manage_users.py', 'init', 'admin']), \
                     patch.object(manager.getpass, 'getpass', return_value='test-password-123'), \
                     patch('builtins.print'):
                    manager.main()
                users = json.loads((root / 'users.json').read_text())
                self.assertEqual(users['admin']['role'], 'admin')
                self.assertTrue(check_password_hash(users['admin']['password_hash'], 'test-password-123'))
                secret = (root / 'secret.key').read_text()
                self.assertGreaterEqual(len(secret), 32)
                for name in ('secret.key', 'users.json'):
                    self.assertEqual(stat.S_IMODE((root / name).stat().st_mode), 0o600)
                with patch('sys.argv', ['manage_users.py', 'set', 'operator', '--role', 'operator']), \
                     patch.object(manager.getpass, 'getpass', return_value='other-test-password'), \
                     patch('builtins.print'):
                    manager.main()
                self.assertEqual((root / 'secret.key').read_text(), secret)
                self.assertEqual(json.loads((root / 'users.json').read_text())['operator']['role'], 'operator')


if __name__ == '__main__':
    unittest.main()
