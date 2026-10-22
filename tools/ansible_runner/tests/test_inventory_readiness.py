"""Execute the real readiness tasks with Ansible and a deterministic API stub."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[3]
PLAYBOOK = ROOT / 'workflows/network_devices_info/playbook'


class InventoryReadinessTests(unittest.TestCase):
    def run_case(self, mode, identifiers=None, timeout=10, override=None, retries=2):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tasks').mkdir()
            (root / 'actions').mkdir()
            for source in (PLAYBOOK / 'tasks').glob('*.yml'):
                tasks = yaml.safe_load(source.read_text())
                for task in tasks:
                    if 'ansible.builtin.uri' in task:
                        task['fake_inventory'] = task.pop('ansible.builtin.uri')
                (root / 'tasks' / source.name).write_text(yaml.safe_dump(tasks))
            (root / 'actions/fake_inventory.py').write_text('''
import json
from pathlib import Path
from ansible.plugins.action import ActionBase
class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        path = Path(task_vars['counts_path'])
        counts = json.loads(path.read_text()) if path.exists() else {}
        ip = task_vars['readiness_ip']
        counts[ip] = counts.get(ip, 0) + 1
        path.write_text(json.dumps(counts))
        mode = task_vars['stub_mode']
        if mode == 'api_error':
            return dict(status=503, failed=True, msg='Simulated API outage')
        if mode == 'empty':
            return dict(status=200, json=dict(response=[]))
        ready = mode == 'ready' or (mode == 'transition' and counts[ip] > 1) or (mode == 'second_unready' and ip.endswith('.1'))
        device = dict(managementIpAddress=ip, collectionStatus='Managed' if ready else 'In Progress',
                      managementState='Managed', reachabilityStatus='Reachable', managedAtleastOnce=True,
                      deviceSupportLevel='Supported', serialNumber='SERIAL', platformId='PLATFORM',
                      inventoryStatusDetail='<status><general code="SUCCESS"/></status>')
        return dict(status=200, json=dict(response=[device]))
''')
            original = yaml.safe_load((PLAYBOOK / 'network_devices_info_playbook.yml').read_text())[0]['tasks']
            tasks = original[4:8]
            # Keep the production selector, extraction and include logic; stub authentication only.
            tasks[2] = dict(name=tasks[2]['name'], when=tasks[2]['when'],
                            **{'ansible.builtin.set_fact': {'readiness_auth': {'json': {'Token': 'test'}}}})
            tasks.append({'name': 'Reached downstream module', 'ansible.builtin.copy':
                          {'content': 'ready', 'dest': str(root / 'downstream')}})
            query = dict(device_identifier=identifiers or [{'ip_address': ['192.0.2.1', '192.0.2.2']}],
                         timeout=timeout, retries=retries, interval=1)
            play = [dict(hosts='localhost', gather_facts=False, connection='local',
                         vars=dict(network_devices_info_details=[{'network_devices': [query]}],
                                   catalyst_center_login=dict(catalystcenter_host='example.test',
                                                              catalystcenter_port=443, catalystcenter_verify=True),
                                   stub_mode=mode, counts_path=str(root / 'counts.json')),
                         tasks=tasks)]
            if override is not None:
                play[0]['vars']['network_devices_info_wait_for_readiness'] = override
            (root / 'test.yml').write_text(yaml.safe_dump(play))
            env = dict(os.environ, ANSIBLE_ACTION_PLUGINS=str(root / 'actions'),
                       ANSIBLE_LOCAL_TEMP=str(root / 'local'), ANSIBLE_REMOTE_TEMP=str(root / 'remote'),
                       ANSIBLE_NOCOLOR='1', OBJC_DISABLE_INITIALIZE_FORK_SAFETY='YES')
            result = subprocess.run([str(Path(sys.executable).parent / 'ansible-playbook'), '-i', 'localhost,',
                                     str(root / 'test.yml'), '-e', 'ansible_python_interpreter=' + sys.executable],
                                    env=env, capture_output=True, text=True, timeout=40)
            counts = json.loads((root / 'counts.json').read_text()) if (root / 'counts.json').exists() else {}
            return result, counts, (root / 'downstream').exists()

    def test_existing_yaml_waits_for_both_ips_without_flag(self):
        result, counts, downstream = self.run_case('transition')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(counts, {'192.0.2.1': 2, '192.0.2.2': 2})
        self.assertTrue(downstream)

    def test_already_ready_devices_proceed(self):
        result, counts, downstream = self.run_case('ready')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(set(counts.values()), {1})
        self.assertTrue(downstream)

    def test_unready_devices_block_downstream(self):
        result, counts, downstream = self.run_case('unready', timeout=1)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(counts, result.stdout + result.stderr)
        self.assertFalse(downstream)

    def test_missing_devices_block_downstream(self):
        result, counts, downstream = self.run_case('empty')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(counts, result.stdout + result.stderr)
        self.assertFalse(downstream)

    def test_one_ready_device_does_not_hide_second_unready_device(self):
        result, counts, downstream = self.run_case('second_unready', timeout=1)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(counts['192.0.2.1'], 1)
        self.assertGreater(counts['192.0.2.2'], 1)
        self.assertFalse(downstream)

    def test_api_errors_block_downstream(self):
        result, counts, downstream = self.run_case('api_error', timeout=1)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(counts, result.stdout + result.stderr)
        self.assertFalse(downstream)

    def test_explicit_diagnostic_opt_out_is_preserved(self):
        result, counts, downstream = self.run_case('unready', override=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(counts)
        self.assertTrue(downstream)

    def test_invalid_controls_fail_before_inventory_lookup(self):
        result, counts, downstream = self.run_case('ready', retries=0)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(counts)
        self.assertFalse(downstream)

    def test_non_ip_query_retains_information_only_behavior(self):
        result, counts, downstream = self.run_case('ready', [{'hostname': ['switch']}])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(counts)
        self.assertTrue(downstream)


if __name__ == '__main__':
    unittest.main()
