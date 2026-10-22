import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import yaml


spec = importlib.util.spec_from_file_location("runner_app", Path(__file__).parents[1] / "app.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class EmbeddedInventoryTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(runner.app.config, TESTING=True, RUNNER_TEST_AUTH_BYPASS=True))
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.inventory = {"all": {"children": {"catalyst_center_hosts": {
            "vars": {"lab_setting": "inherited"},
            "hosts": {"catc": {"ansible_connection": "local", "password": "test-secret"}},
        }}}}
        self.inputs = {"inventory": self.inventory, "workflow_details": [{"name": "test"}]}
        self.write("combined.yml", self.inputs)
        self.write("vars.yml", {"workflow_details": [{"name": "test"}]})
        self.write("hosts.yml", self.inventory)
        self.write("play.yml", [{"hosts": "catalyst_center_hosts", "tasks": []}])
        (self.root / "schema.yml").write_text("workflow_details: list(include('entry'))\n---\nentry:\n  name: str()\n")
        self.client = runner.app.test_client()
        self.enterContext(patch.object(runner, "_resolve_git_source", return_value=self.root))
        self.enterContext(patch.object(runner, "_resolve_source_file", side_effect=self.resolve))

    def write(self, name, content):
        (self.root / name).write_text(yaml.safe_dump(content))

    def resolve(self, name, *args, **kwargs):
        return self.root / name if name and (self.root / name).is_file() else None

    def build(self, **overrides):
        return runner._build_run_job({
            "playbook": "play.yml", "vars_file": "combined.yml", "managed_venv": False,
            **overrides,
        })

    def validate(self, **overrides):
        return self.client.post("/api/validate", json={
            "schema": "schema.yml", "data": "combined.yml", "require_embedded_inventory": True,
            **overrides,
        })

    def test_combined_schema_keeps_workflow_strict(self):
        self.assertTrue(self.validate().json["ok"])
        self.write("combined.yml", {**self.inputs, "unexpected": True})
        self.assertFalse(self.validate().json["ok"])

    def test_workflow_errors_still_fail(self):
        self.write("combined.yml", {"inventory": self.inventory, "workflow_details": "wrong"})
        self.assertFalse(self.validate().json["ok"])

    def test_separate_files_still_work(self):
        self.assertTrue(self.validate(data="vars.yml", require_embedded_inventory=False).json["ok"])
        job, _ = self.build(inventory="hosts.yml", vars_file="vars.yml")
        self.assertIsNone(job.embedded_inventory)
        self.assertEqual(job.argv[2], str(self.root / "hosts.yml"))

    def test_explicit_inventory_takes_precedence(self):
        job, _ = self.build(inventory="hosts.yml")
        self.assertIsNone(job.embedded_inventory)
        self.assertEqual(job.metadata["inventory"], "hosts.yml")

    def test_invalid_selected_inventory_does_not_fall_back(self):
        job, error = self.build(inventory="missing.yml")
        self.assertIsNone(job)
        self.assertEqual(error, "Inventory file not found")

    def test_missing_inventory_fails_validation_and_launch(self):
        self.assertFalse(self.validate(data="vars.yml").json["ok"])
        job, error = self.build(vars_file="vars.yml")
        self.assertIsNone(job)
        self.assertIn("inventory", error)

    def test_bad_inventory_shapes_rejected(self):
        for inventory in ([], {}, {"all": {"hosts": ["catc"]}}, {"all": {"hosts": {}}}):
            with self.subTest(inventory=inventory):
                self.write("combined.yml", {**self.inputs, "inventory": inventory})
                self.assertFalse(self.validate().json["ok"])
                self.assertIsNone(self.build()[0])

    def test_recursive_group_rejected(self):
        group = {}
        group["children"] = {"loop": group}
        with self.assertRaises(ValueError):
            runner._embedded_inventory({"inventory": {"all": group}})

    def test_customize_returns_combined_file(self):
        result = self.client.get("/api/file?path=combined.yml")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(yaml.safe_load(result.json["content"]), self.inputs)
        updated = {**self.inputs, "workflow_details": [{"name": "edited"}]}
        result = self.client.put("/api/file", json={"path": "combined.yml", "content": yaml.safe_dump(updated)})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(runner._read_workflow_inputs(self.root / "combined.yml"), updated)
        self.assertTrue(self.validate().json["ok"])

    def test_runtime_inventory_is_private_and_cleaned(self):
        job, _ = self.build()
        self.assertTrue(job.metadata["inventory_embedded"])
        self.assertEqual(job.metadata["inventory"], "")
        self.assertNotIn("test-secret", json.dumps(job.info()))
        generated = []

        def start(argv, **kwargs):
            path = Path(argv[2])
            generated.append(path)
            self.assertEqual(yaml.safe_load(path.read_text()), self.inventory)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            raise OSError("simulated process start failure")

        with patch.object(runner.subprocess, "Popen", side_effect=start):
            runner._exec(job)
        self.assertEqual(job.status, "failed")
        self.assertFalse(generated[0].parent.exists())

    def test_queued_cancel_does_not_create_inventory(self):
        job, _ = self.build()
        job.status = "cancelled"
        with patch.object(runner.tempfile, "TemporaryDirectory") as temporary:
            runner._exec(job)
        temporary.assert_not_called()


if __name__ == "__main__":
    unittest.main()
