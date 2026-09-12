from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
WORKER = ROOT / "bin/hermes-worker"


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.state_root = self.root / "state"
        self.fake_log = self.root / "fake-hermes.json"
        self.fake_hermes = self.root / "fake-hermes"
        self.fake_hermes.write_text(
            """#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys

args = sys.argv[1:]
if args == ["--version"]:
    print("Hermes Agent fake")
    raise SystemExit(0)
if args[:2] == ["plugins", "list"]:
    print("codex-worker-guard")
    raise SystemExit(0)
if args[:2] == ["plugins", "capabilities"]:
    print("declared: (none)")
    raise SystemExit(0)

workspace = pathlib.Path(args[args.index("--in") + 1])
payload = {"args": args}
if (workspace / ".git").exists():
    payload["workspace_head"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=workspace, text=True
    ).strip()
pathlib.Path(os.environ["FAKE_HERMES_LOG"]).write_text(json.dumps(payload))
if os.environ.get("FAKE_HERMES_WRITE") == "1":
    (workspace / "candidate.txt").write_text("candidate\\n")
if "--usage-file" in args:
    pathlib.Path(args[args.index("--usage-file") + 1]).write_text("{}\\n")
print("fake result")
raise SystemExit(int(os.environ.get("FAKE_HERMES_EXIT", "0")))
"""
        )
        self.fake_hermes.chmod(0o755)

        self.home = self.root / "home"
        (self.home / ".agents/skills/local-worker").mkdir(parents=True)
        (self.home / ".agents/skills/local-worker/SKILL.md").write_text("test\n")
        (self.home / ".hermes/plugins/codex-worker-guard").mkdir(parents=True)

        self.env = os.environ.copy()
        self.env.update(
            {
                "HOME": str(self.home),
                "HERMES_BIN": str(self.fake_hermes),
                "HERMES_WORKER_STATE_ROOT": str(self.state_root),
                "FAKE_HERMES_LOG": str(self.fake_log),
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_worker(self, mode: str, repo: Path | None = None, **env_overrides):
        env = self.env | {key: str(value) for key, value in env_overrides.items()}
        command = [str(WORKER), mode]
        if repo is not None:
            command += ["--repo", str(repo)]
        return subprocess.run(
            command,
            input="bounded task\n",
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def fake_args(self):
        return json.loads(self.fake_log.read_text())["args"]

    def fake_record(self):
        return json.loads(self.fake_log.read_text())

    def init_repo(self):
        repo = self.root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
        (repo / "tracked.txt").write_text("baseline\n")
        subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True)
        subprocess.run(
            [
                "git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "-q", "-m", "baseline",
            ],
            cwd=repo,
            check=True,
        )
        return repo

    def test_mode_toolsets_use_least_capability(self):
        expected = {
            "scout": "file,terminal",
            "research": "web,file,terminal",
            "review": "file,terminal",
        }
        for mode, toolsets in expected.items():
            with self.subTest(mode=mode):
                result = self.run_worker(mode, self.root)
                self.assertEqual(result.returncode, 0, result.stderr)
                args = self.fake_args()
                self.assertEqual(args[args.index("--toolsets") + 1], toolsets)

    def test_dirty_prototype_fails_before_hermes(self):
        repo = self.init_repo()
        (repo / "uncommitted.txt").write_text("dirty\n")

        result = self.run_worker("prototype", repo)

        self.assertEqual(result.returncode, 2)
        self.assertIn("requires a clean worktree", result.stderr)
        self.assertFalse(self.fake_log.exists())

    def test_clean_prototype_records_exact_base_and_owns_worktree(self):
        repo = self.init_repo()
        base_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip()

        result = self.run_worker("prototype", repo)

        self.assertEqual(result.returncode, 0, result.stderr)
        meta_path = next(self.state_root.glob("*/meta.json"))
        meta = json.loads(meta_path.read_text())
        self.assertEqual(meta["base_sha"], base_sha)
        self.assertEqual(self.fake_record()["workspace_head"], base_sha)
        self.assertEqual(meta["repo"], str(repo))
        self.assertTrue(meta["worktree"])
        self.assertNotIn("--worktree", self.fake_args())
        self.assertFalse(Path(meta["workspace"]).exists())
        self.assertIn("empty prototype worktree removed", result.stderr)

    def test_changed_prototype_worktree_is_retained_for_review(self):
        repo = self.init_repo()

        result = self.run_worker("prototype", repo, FAKE_HERMES_WRITE=1)

        self.assertEqual(result.returncode, 0, result.stderr)
        meta = json.loads(next(self.state_root.glob("*/meta.json")).read_text())
        workspace = Path(meta["workspace"])
        self.assertEqual((workspace / "candidate.txt").read_text(), "candidate\n")
        self.assertIn("prototype worktree retained for review", result.stderr)

    def test_hermes_exit_code_propagates(self):
        result = self.run_worker("scout", self.root, FAKE_HERMES_EXIT=23)

        self.assertEqual(result.returncode, 23)
        self.assertIn("hermes-worker failed rc=23", result.stderr)

    def test_run_creates_metadata_and_result_files(self):
        result = self.run_worker("scout", self.root)

        self.assertEqual(result.returncode, 0, result.stderr)
        run_dir = next(path for path in self.state_root.iterdir() if path.is_dir())
        meta = json.loads((run_dir / "meta.json").read_text())
        self.assertEqual(meta["mode"], "scout")
        self.assertEqual(meta["toolsets"], "file,terminal")
        self.assertTrue(meta["mutation_guarded"])
        self.assertEqual((run_dir / "result.txt").read_text(), "fake result\n")
        self.assertTrue((run_dir / "usage.json").is_file())

    def test_doctor_fails_when_hermes_is_missing(self):
        result = self.run_worker("doctor", HERMES_BIN=self.root / "missing-hermes")

        self.assertEqual(result.returncode, 2)
        self.assertIn("Hermes executable not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
