import importlib.util
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch


spec = importlib.util.spec_from_file_location("review_runner", Path(__file__).parents[1] / "app.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(runner.app.config, TESTING=True, RUNNER_TEST_AUTH_BYPASS=True))
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name).resolve()
        self.project = self.root / "project"
        self.git = self.root / "git"
        self.project.mkdir()
        self.git.mkdir()
        self.enterContext(patch.object(runner, "PROJECT_ROOT", self.project))
        self.enterContext(patch.object(runner, "HOME_DIR", self.root))
        self.enterContext(patch.object(runner, "_jobs", {}))
        self.enterContext(patch.object(runner, "_cancelled_suites", set()))
        self.client = runner.app.test_client()

    def test_git_source_cannot_fall_back_to_local_file(self):
        (self.project / "vars.yml").write_text("local: true\n")
        self.assertIsNone(runner._resolve_source_file("vars.yml", self.git))
        self.assertIsNone(runner._resolve_source_file(str(self.project / "vars.yml"), self.git))

    def test_git_write_changes_only_selected_repository(self):
        (self.project / "vars.yml").write_text("local: true\n")
        (self.git / "vars.yml").write_text("git: true\n")
        with patch.object(runner, "_resolve_git_source", return_value=self.git):
            response = self.client.put("/api/file", json={
                "path": "vars.yml", "content": "edited: true\n",
                "source": {"kind": "git", "id": "repo_0123456789ab"},
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual((self.git / "vars.yml").read_text(), "edited: true\n")
        self.assertEqual((self.project / "vars.yml").read_text(), "local: true\n")

    def test_traversal_symlinks_and_non_yaml_denied(self):
        outside = self.root / "outside.yml"
        outside.write_text("secret: true\n")
        (self.git / "escape.yml").symlink_to(outside)
        for name in ("../outside.yml", "escape.yml", str(outside), ".git/config", "file.txt"):
            with self.subTest(name=name):
                self.assertIsNone(runner._resolve_source_file(name, self.git, must_exist=False))
        non_yaml = self.project / "settings.txt"
        non_yaml.write_text("private")
        self.assertIsNone(runner._resolve_source_file(str(non_yaml), self.project))

    def test_unexpected_validation_errors_are_not_exposed(self):
        import yamale

        with patch.object(runner, "_resolve_source_file", return_value=self.project / "input.yml"), \
                patch.object(yamale, "make_schema", side_effect=RuntimeError("PRIVATE server path/token")), \
                patch.object(runner.app.logger, "exception") as logged:
            response = self.client.post("/api/validate", json={"schema": "schema.yml", "data": "vars.yml"})
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("PRIVATE", response.get_data(as_text=True))
        logged.assert_called_once()

    def test_file_io_errors_do_not_expose_server_paths(self):
        (self.project / "vars.yml").write_text("test: true\n")
        for method, operation in (("get", "read_text"), ("put", "write_text")):
            with self.subTest(method=method), \
                    patch.object(Path, operation, side_effect=PermissionError("PRIVATE path/token")), \
                    patch.object(runner.app.logger, "exception") as logged:
                if method == "get":
                    response = self.client.get("/api/file?path=vars.yml")
                else:
                    response = self.client.put("/api/file", json={"path": "vars.yml", "content": "test: false"})
                self.assertEqual(response.status_code, 500)
                self.assertNotIn("PRIVATE", response.get_data(as_text=True))
                logged.assert_called_once()

    def test_validation_value_errors_are_not_exposed(self):
        import yamale

        for operation in ("schema", "inputs", "validation"):
            with self.subTest(operation=operation), \
                    patch.object(runner, "_resolve_source_file", return_value=self.project / "input.yml"), \
                    patch.object(yamale, "make_schema", return_value=object()) as make_schema, \
                    patch.object(runner, "_read_workflow_inputs", return_value={"details": []}) as read_inputs, \
                    patch.object(yamale, "validate") as validate, \
                    patch.object(runner.app.logger, "exception") as logged:
                source = {"schema": make_schema, "inputs": read_inputs, "validation": validate}[operation]
                source.side_effect = ValueError("PRIVATE /server/path with credential-token")
                response = self.client.post("/api/validate", json={"schema": "schema.yml", "data": "vars.yml"})
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.json["ok"])
                self.assertIn("valid YAML mapping", response.json["out"])
                self.assertNotIn("PRIVATE", response.get_data(as_text=True))
                self.assertNotIn("credential-token", response.get_data(as_text=True))
                logged.assert_called_once()

    def test_queued_cancel_never_starts_after_semaphore_release(self):
        job = runner.Job("queued", ["unused"], str(self.root))
        runner._jobs[job.id] = job
        semaphore = threading.Semaphore(0)
        worker = threading.Thread(target=runner._exec_with_semaphore, args=(job, semaphore))
        with patch.object(runner.subprocess, "Popen") as start:
            worker.start()
            self.assertEqual(self.client.post("/api/run/queued/cancel").json["status"], "cancelled")
            semaphore.release()
            worker.join(2)
            self.assertFalse(worker.is_alive())
            start.assert_not_called()

    def test_cancel_serializes_with_process_creation(self):
        job = runner.Job("starting", ["unused"], str(self.root))
        entered, release = threading.Event(), threading.Event()
        proc = Mock(pid=123, stdout=None, returncode=-15)

        def start(*args, **kwargs):
            entered.set()
            self.assertTrue(release.wait(2))
            return proc

        with patch.object(runner.subprocess, "Popen", side_effect=start), \
                patch.object(runner.os, "getpgid", return_value=123), \
                patch.object(runner.os, "killpg") as kill:
            worker = threading.Thread(target=runner._exec, args=(job,))
            worker.start()
            self.assertTrue(entered.wait(2))
            stopper = threading.Thread(target=runner._cancel_job, args=(job,))
            stopper.start()
            # Keep execution active until the cancellation thread has signalled it.
            proc.wait.side_effect = lambda: stopper.join(2)
            release.set()
            worker.join(3)
            stopper.join(3)
            self.assertFalse(worker.is_alive())
            self.assertFalse(stopper.is_alive())
            kill.assert_called_once_with(123, runner.signal.SIGTERM)
            self.assertEqual(job.status, "cancelled")

    def test_suite_stop_blocks_future_and_late_submissions(self):
        queued = runner.Job("queued", ["unused"], str(self.root), metadata={"suite_launch_id": "suite"})
        runner._jobs[queued.id] = queued
        self.client.post("/api/run/suite/suite/cancel")
        with patch.object(runner, "_build_run_job") as build:
            runner._exec_suite_sequence([{"suite_launch_id": "suite"}], "continue")
            build.assert_not_called()
        late = runner.Job("late", ["unused"], str(self.root), metadata={"suite_launch_id": "suite"})
        with patch.object(runner.subprocess, "Popen") as start:
            runner._exec(late)
            start.assert_not_called()
        self.assertEqual(queued.status, "cancelled")
        self.assertEqual(late.status, "cancelled")

    def test_real_running_process_is_terminated(self):
        job = runner.Job("real", [sys.executable, "-c", "import time; time.sleep(30)"], str(self.root))
        worker = threading.Thread(target=runner._exec, args=(job,))
        worker.start()
        try:
            deadline = time.monotonic() + 3
            while job.proc is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertIsNotNone(job.proc)
            runner._cancel_job(job)
            worker.join(3)
            self.assertFalse(worker.is_alive())
            self.assertEqual(job.status, "cancelled")
            self.assertIsNotNone(job.proc.poll())
        finally:
            if job.proc and job.proc.poll() is None:
                job.proc.kill()
            worker.join(3)


if __name__ == "__main__":
    unittest.main()
