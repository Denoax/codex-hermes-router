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
if args == ["chat", "--help"]:
    print("usage: hermes chat" + ("" if os.environ.get("FAKE_NO_IGNORE_RULES") == "1" else " [--ignore-rules]"))
    raise SystemExit(0)
if args[:2] == ["plugins", "list"]:
    if "FAKE_PLUGIN_JSON" in os.environ:
        print(os.environ["FAKE_PLUGIN_JSON"])
        raise SystemExit(0)
    status = os.environ.get("FAKE_GUARD_STATUS", "enabled")
    print(json.dumps([{"name": "codex-worker-guard", "status": status}]))
    raise SystemExit(0)
if args[:2] == ["plugins", "doctor"]:
    raise SystemExit(int(os.environ.get("FAKE_GUARD_DOCTOR_EXIT", "0")))
if args[:2] == ["plugins", "capabilities"]:
    print(os.environ.get("FAKE_CAPABILITIES", "declared: (none)"))
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
if os.environ.get("FAKE_HERMES_COMMIT") == "1":
    (workspace / "candidate.txt").write_text("committed candidate\\n")
    subprocess.run(["git", "add", "candidate.txt"], cwd=workspace, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
         "commit", "-q", "-m", "candidate"],
        cwd=workspace,
        check=True,
    )
if os.environ.get("FAKE_BREAK_GIT") == "1":
    (workspace / ".git").unlink()
if "--usage-file" in args and os.environ.get("FAKE_NO_USAGE") != "1":
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
        command = ["/usr/bin/bash", str(WORKER), mode]
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
            "research": "web",
            "review": "file,terminal",
        }
        for mode, toolsets in expected.items():
            with self.subTest(mode=mode):
                result = self.run_worker(mode, self.root)
                self.assertEqual(result.returncode, 0, result.stderr)
                args = self.fake_args()
                self.assertEqual(args[args.index("--toolsets") + 1], toolsets)
                self.assertEqual(args[args.index("chat") + 1], "--oneshot")
                self.assertIn("--ignore-rules", args)
                self.assertNotIn("-z", args)

    def test_direct_worker_does_not_require_codex_skill(self):
        (self.home / ".agents/skills/local-worker/SKILL.md").unlink()

        result = self.run_worker("scout", self.root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.fake_log.exists())

    def test_worker_fails_closed_when_guard_is_disabled(self):
        result = self.run_worker("scout", self.root, FAKE_GUARD_STATUS="disabled")

        self.assertEqual(result.returncode, 2)
        self.assertIn("guard plugin is not enabled", result.stderr)
        self.assertFalse(self.fake_log.exists())

    def test_worker_fails_closed_when_guard_hook_is_invalid(self):
        result = self.run_worker("scout", self.root, FAKE_GUARD_DOCTOR_EXIT=1)

        self.assertEqual(result.returncode, 2)
        self.assertIn("guard plugin hook validation failed", result.stderr)
        self.assertFalse(self.fake_log.exists())

    def test_worker_fails_closed_on_invalid_plugin_status(self):
        result = self.run_worker("scout", self.root, FAKE_PLUGIN_JSON="not-json")

        self.assertEqual(result.returncode, 2)
        self.assertIn("guard plugin is not enabled", result.stderr)
        self.assertFalse(self.fake_log.exists())

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

    def test_committed_prototype_is_retained_for_review(self):
        repo = self.init_repo()
        base_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip()

        result = self.run_worker("prototype", repo, FAKE_HERMES_COMMIT=1)

        self.assertEqual(result.returncode, 0, result.stderr)
        meta = json.loads(next(self.state_root.glob("*/meta.json")).read_text())
        workspace = Path(meta["workspace"])
        candidate_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=workspace, text=True
        ).strip()
        self.assertNotEqual(candidate_sha, base_sha)
        self.assertEqual(meta["candidate_head"], candidate_sha)
        self.assertTrue(meta["candidate_changed"])
        self.assertIn(f"candidate: {candidate_sha}", result.stderr)

    def test_failed_committed_prototype_is_still_retained(self):
        repo = self.init_repo()

        result = self.run_worker(
            "prototype", repo, FAKE_HERMES_COMMIT=1, FAKE_HERMES_EXIT=23
        )

        self.assertEqual(result.returncode, 23)
        meta = json.loads(next(self.state_root.glob("*/meta.json")).read_text())
        workspace = Path(meta["workspace"])
        self.assertTrue(workspace.exists())
        self.assertEqual(meta["exit_code"], 23)
        self.assertTrue(meta["candidate_changed"])
        self.assertNotEqual(meta["candidate_head"], meta["base_sha"])

    def test_unverifiable_prototype_state_is_preserved(self):
        repo = self.init_repo()

        result = self.run_worker("prototype", repo, FAKE_BREAK_GIT=1)

        self.assertEqual(result.returncode, 0, result.stderr)
        meta = json.loads(next(self.state_root.glob("*/meta.json")).read_text())
        self.assertTrue(Path(meta["workspace"]).exists())
        self.assertIsNone(meta["candidate_changed"])
        self.assertIn("state could not be verified", result.stderr)

    def test_failed_run_is_recorded_without_usage_and_counted(self):
        result = self.run_worker(
            "scout", self.root, FAKE_HERMES_EXIT=23, FAKE_NO_USAGE=1
        )

        self.assertEqual(result.returncode, 23)
        self.assertIn("hermes-worker failed rc=23", result.stderr)
        meta = json.loads(next(self.state_root.glob("*/meta.json")).read_text())
        self.assertEqual(meta["exit_code"], 23)
        self.assertFalse(meta["usage_available"])
        self.assertIsInstance(meta["duration_ms"], int)

        stats = self.run_worker("stats")
        self.assertEqual(stats.returncode, 0, stats.stderr)
        self.assertIn("runs=1", stats.stdout)
        self.assertIn("failed_runs=1", stats.stdout)
        self.assertIn("runs_with_usage=0", stats.stdout)

    def test_run_creates_metadata_and_result_files(self):
        result = self.run_worker("scout", self.root)

        self.assertEqual(result.returncode, 0, result.stderr)
        run_dir = next(path for path in self.state_root.iterdir() if path.is_dir())
        meta = json.loads((run_dir / "meta.json").read_text())
        self.assertEqual(meta["mode"], "scout")
        self.assertEqual(meta["toolsets"], "file,terminal")
        self.assertTrue(meta["mutation_guarded"])
        self.assertEqual(meta["exit_code"], 0)
        self.assertTrue(meta["usage_available"])
        self.assertIsInstance(meta["finished_unix"], int)
        self.assertIsInstance(meta["duration_ms"], int)
        self.assertEqual((run_dir / "result.txt").read_text(), "fake result\n")
        self.assertTrue((run_dir / "usage.json").is_file())

        stats = self.run_worker("stats")
        self.assertEqual(stats.returncode, 0, stats.stderr)
        self.assertIn("runs_with_usage=1", stats.stdout)

    def test_stats_counts_incomplete_run_metadata(self):
        run_dir = self.state_root / "incomplete"
        run_dir.mkdir(parents=True)
        (run_dir / "meta.json").write_text(
            json.dumps({"mode": "review", "exit_code": None})
        )

        stats = self.run_worker("stats")

        self.assertEqual(stats.returncode, 0, stats.stderr)
        self.assertIn("runs=1", stats.stdout)
        self.assertIn("review=1", stats.stdout)
        self.assertIn("incomplete_runs=1", stats.stdout)

    def test_doctor_fails_when_hermes_is_missing(self):
        result = self.run_worker("doctor", HERMES_BIN=self.root / "missing-hermes")

        self.assertEqual(result.returncode, 2)
        self.assertIn("Hermes executable not found", result.stderr)

    def test_doctor_fails_when_skill_is_missing(self):
        (self.home / ".agents/skills/local-worker/SKILL.md").unlink()

        result = self.run_worker("doctor")

        self.assertEqual(result.returncode, 2)
        self.assertIn("Codex worker skill missing", result.stderr)

    def test_doctor_fails_when_guard_is_missing(self):
        (self.home / ".hermes/plugins/codex-worker-guard").rmdir()

        result = self.run_worker("doctor")

        self.assertEqual(result.returncode, 2)
        self.assertIn("guard plugin missing", result.stderr)

    def test_doctor_fails_when_guard_is_disabled(self):
        result = self.run_worker("doctor", FAKE_GUARD_STATUS="disabled")

        self.assertEqual(result.returncode, 2)
        self.assertIn("guard plugin is not enabled", result.stderr)

    def test_doctor_fails_without_required_rule_isolation(self):
        result = self.run_worker("doctor", FAKE_NO_IGNORE_RULES=1)

        self.assertEqual(result.returncode, 2)
        self.assertIn("does not support required --ignore-rules", result.stderr)

    def test_doctor_fails_when_python_is_missing(self):
        empty_path = self.root / "empty-path"
        empty_path.mkdir()

        result = self.run_worker("doctor", PATH=empty_path)

        self.assertEqual(result.returncode, 2)
        self.assertIn("Python 3 executable not found", result.stderr)

    def test_doctor_fails_when_git_is_missing(self):
        python_only_path = self.root / "python-only-path"
        python_only_path.mkdir()
        (python_only_path / "python3").symlink_to("/usr/bin/python3")

        result = self.run_worker("doctor", PATH=python_only_path)

        self.assertEqual(result.returncode, 2)
        self.assertIn("Git executable not found", result.stderr)

    def test_doctor_rejects_unnecessary_tool_override(self):
        result = self.run_worker(
            "doctor", FAKE_CAPABILITIES="tools.override: granted"
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unnecessary tools.override", result.stderr)

    def test_doctor_succeeds_for_valid_runtime(self):
        result = self.run_worker("doctor")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Doctor: OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
