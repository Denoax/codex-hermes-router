from __future__ import annotations
import importlib.util
import os
import pathlib
import unittest

PLUGIN = pathlib.Path(__file__).parents[1] / "integrations/hermes/codex-worker-guard/__init__.py"
spec = importlib.util.spec_from_file_location("codex_worker_guard", PLUGIN)
guard = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(guard)

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = dict(os.environ)
        os.environ["HERMES_CODEX_WORKER"] = "1"
        os.environ["HERMES_WORKER_MODE"] = "scout"
        os.environ["HERMES_WORKER_READONLY"] = "1"

    def tearDown(self):
        os.environ.clear(); os.environ.update(self.old)

    def call(self, command: str):
        return guard.pre_tool_call("terminal", {"command": command})

    def test_inert_outside_worker(self):
        os.environ.pop("HERMES_CODEX_WORKER", None)
        self.assertIsNone(self.call("git push origin main"))

    def test_safe_read_allowed(self):
        self.assertIsNone(self.call("git status --short"))
        self.assertIsNone(self.call("rg -n TODO ."))

    def test_direct_write_tools_blocked_readonly(self):
        self.assertEqual(guard.pre_tool_call("write_file", {"path":"x","content":"y"})["action"], "block")
        self.assertEqual(guard.pre_tool_call("patch", {"path":"x"})["action"], "block")

    def test_shell_write_blocked_readonly(self):
        self.assertEqual(self.call("touch /tmp/x")["action"], "block")
        self.assertEqual(self.call("printf hi > /tmp/x")["action"], "block")
        self.assertEqual(self.call("git add README.md")["action"], "block")

    def test_remote_actions_blocked(self):
        for command in [
            "git push origin main", "gh pr merge 1", "npm publish",
            "terraform apply", "kubectl apply -f prod.yaml", "sudo id",
        ]:
            with self.subTest(command=command):
                self.assertEqual(self.call(command)["action"], "block")

    def test_prototype_can_write_locally_but_not_push(self):
        os.environ["HERMES_WORKER_MODE"] = "prototype"
        os.environ["HERMES_WORKER_READONLY"] = "0"
        self.assertIsNone(self.call("touch local-file"))
        self.assertEqual(self.call("git push origin main")["action"], "block")

if __name__ == "__main__":
    unittest.main()
