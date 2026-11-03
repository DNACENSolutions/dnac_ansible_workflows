"""Offline wrapper tests. The stub collection cannot contact a controller."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yamale
import yaml

WORKFLOW = Path(__file__).resolve().parents[1]


class BorderCvpTests(unittest.TestCase):
    def test_input_schema(self):
        schema = yamale.make_schema(str(WORKFLOW / 'schema/switch_refresh_sda_fabric_border_schema.yml'))
        sample = yaml.safe_load((WORKFLOW / 'vars/switch_refresh_sda_fabric_border_input.yml').read_text())
        yamale.validate(schema, [(sample, 'sample')])
        for key, value in [('switch_refresh_sda_fabric_border_cutover_approved', 'true'),
                           ('switch_refresh_sda_fabric_border_batches', []),
                           ('switch_refresh_sda_fabric_border_inventory_readiness_timeout', 0)]:
            invalid = copy.deepcopy(sample)
            invalid[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                yamale.validate(schema, [(invalid, 'invalid')])

    def run_wrapper(self, phase, *, legacy=False, approved=False, resume=False, from_inventory=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / 'ansible_collections/cisco/catalystcenter/roles/switch_refresh_sda_fabric_border/tasks'
            tasks.mkdir(parents=True)
            marker = root / 'role-called'
            stub = [{'name': 'Verify resolved role parameters', 'ansible.builtin.assert': {'that': [
                'catalystcenter_host == "controller.example.test"',
                'catalystcenter_username == "example-user"',
                'catalystcenter_password == "example-password"',
                'catalystcenter_port | int == 8443',
                'catalystcenter_verify | bool',
                'catalystcenter_log_level == "WARNING"',
                'switch_refresh_sda_fabric_border_phase == expected_phase',
                '(switch_refresh_sda_fabric_border_cutover_approved | type_debug) == "bool"',
                'switch_refresh_sda_fabric_border_cutover_approved == expected_approval',
                'switch_refresh_sda_fabric_border_resume_from_manifest == expected_resume']}},
                {'name': 'Record stub role invocation', 'ansible.builtin.copy': {'content': 'called', 'dest': str(marker)}}]
            (tasks / 'main.yml').write_text(yaml.safe_dump(stub))
            prefix = 'catalystcenter_' if legacy else 'catalyst_center_'
            values = {prefix + key: value for key, value in dict(host='controller.example.test',
                      username='example-user', password='example-password', port=8443,
                      verify=True, log_level='WARNING').items()}
            (root / 'inventory.yml').write_text(yaml.safe_dump({'catalyst_center_hosts': {
                'hosts': {'test_controller': values}}}))
            sample = yaml.safe_load((WORKFLOW / 'vars/switch_refresh_sda_fabric_border_input.yml').read_text())
            sample['switch_refresh_sda_fabric_border_cutover_approved'] = approved
            sample['switch_refresh_sda_fabric_border_resume_from_manifest'] = resume
            (root / 'input.yml').write_text(yaml.safe_dump(sample))
            extra = dict(expected_phase=phase, expected_approval=approved if phase == 'cutover' else False,
                         expected_resume=resume if phase == 'cutover' else False,
                         ansible_python_interpreter=sys.executable)
            if from_inventory:
                inventory = yaml.safe_load((root / 'inventory.yml').read_text())
                inventory['catalyst_center_hosts']['hosts']['test_controller'].update(sample)
                (root / 'inventory.yml').write_text(yaml.safe_dump(inventory))
            else:
                extra['VARS_FILE_PATH'] = str(root / 'input.yml')
            env = dict(os.environ, ANSIBLE_COLLECTIONS_PATH=str(root),
                       ANSIBLE_LOCAL_TEMP=str(root / 'local'), ANSIBLE_REMOTE_TEMP=str(root / 'remote'),
                       ANSIBLE_NOCOLOR='1', OBJC_DISABLE_INITIALIZE_FORK_SAFETY='YES')
            result = subprocess.run([str(Path(sys.executable).parent / 'ansible-playbook'),
                '-i', str(root / 'inventory.yml'),
                str(WORKFLOW / 'playbook' / ('switch_refresh_sda_fabric_border_' + phase + '.yml')),
                '-e', json.dumps(extra)], env=env, capture_output=True, text=True, timeout=30)
            return result, marker.exists()

    def test_prepare_both_connection_names_and_safe_controls(self):
        for legacy in (False, True):
            with self.subTest(legacy=legacy):
                result, called = self.run_wrapper('prepare', legacy=legacy, approved=True, resume=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(called)

    def test_inventory_backed_input(self):
        result, called = self.run_wrapper('prepare', from_inventory=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(called)

    def test_cutover_requires_approval_and_typed_controls(self):
        for approved in (False, 'true'):
            with self.subTest(approved=approved):
                result, called = self.run_wrapper('cutover', approved=approved)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(called)

    def test_approved_cutover_and_non_destructive_continuation(self):
        for approved, resume in ((True, False), (True, True), (False, True)):
            with self.subTest(approved=approved, resume=resume):
                result, called = self.run_wrapper('cutover', approved=approved, resume=resume)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(called)


if __name__ == '__main__':
    unittest.main()
