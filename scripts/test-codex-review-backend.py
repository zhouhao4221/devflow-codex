#!/usr/bin/env python3
"""Verify the native Codex review adapter without starting a real Codex run."""

from pathlib import Path
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "plugins" / "rd" / "skills" / "pr" / "scripts" / "run-codex-review.sh"


class CodexReviewBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="devflow-codex-review-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.capture = self.base / "capture"
        self.fake_bin = self.base / "bin"
        self.repo.mkdir()
        self.capture.mkdir()
        self.fake_bin.mkdir()

        self.run_git("init", "-b", "main")
        self.run_git("config", "user.name", "DevFlow Test")
        self.run_git("config", "user.email", "devflow@example.test")
        (self.repo / "example.txt").write_text("base\n")
        self.run_git("add", "example.txt")
        self.run_git("commit", "-m", "base")
        self.base_sha = self.git_output("rev-parse", "HEAD")

        self.run_git("switch", "-c", "feature")
        (self.repo / "example.txt").write_text("base\nfeature\n")
        self.run_git("add", "example.txt")
        self.run_git("commit", "-m", "feature")
        self.head_sha = self.git_output("rev-parse", "HEAD")

        fake_codex = self.fake_bin / "codex"
        fake_codex.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [ \"${1:-}\" = exec ] && [ \"${2:-}\" = review ] && [ \"${3:-}\" = --help ]; then\n"
            "  exit \"${FAKE_CODEX_HELP_STATUS:-0}\"\n"
            "fi\n"
            "printf '%s\\n' \"$*\" > \"$CAPTURE_DIR/args\"\n"
            "pwd > \"$CAPTURE_DIR/cwd\"\n"
            "git rev-parse HEAD > \"$CAPTURE_DIR/head\"\n"
            "cat > \"$CAPTURE_DIR/prompt\"\n"
            "if [ \"${FAKE_CODEX_RUN_STATUS:-0}\" != 0 ]; then\n"
            "  exit \"$FAKE_CODEX_RUN_STATUS\"\n"
            "fi\n"
            "printf '%s\\n' '[P1] example finding'\n"
        )
        fake_codex.chmod(0o755)

    def run_git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, text=True)

    def git_output(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=True, capture_output=True, text=True
        ).stdout.strip()

    def adapter_command(self, base_sha=None):
        return [
            str(ADAPTER),
            "--repo",
            str(self.repo),
            "--base-ref",
            "main",
            "--base-sha",
            base_sha or self.base_sha,
            "--head-sha",
            self.head_sha,
        ]

    def adapter_env(self, **extra):
        env = os.environ.copy()
        env["PATH"] = f"{self.fake_bin}{os.pathsep}{env['PATH']}"
        env["CAPTURE_DIR"] = str(self.capture)
        env.update(extra)
        return env

    def test_runs_at_fixed_head_without_switching_source_worktree(self):
        before_branch = self.git_output("branch", "--show-current")
        result = subprocess.run(
            self.adapter_command(),
            input="Check API compatibility and cite affected lines.\n",
            env=self.adapter_env(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[P1] example finding", result.stdout)
        self.assertEqual((self.capture / "head").read_text().strip(), self.head_sha)
        self.assertEqual(
            (self.capture / "args").read_text().strip(),
            "exec review --ephemeral --base main -",
        )
        self.assertIn("Check API compatibility", (self.capture / "prompt").read_text())
        self.assertNotEqual(Path((self.capture / "cwd").read_text().strip()), self.repo)
        self.assertEqual(self.git_output("branch", "--show-current"), before_branch)
        worktrees = self.git_output("worktree", "list", "--porcelain")
        self.assertEqual(worktrees.count("worktree "), 1)

    def test_rejects_a_base_ref_that_moved(self):
        result = subprocess.run(
            self.adapter_command(base_sha=self.head_sha),
            input="Review this change.\n",
            env=self.adapter_env(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 65)
        self.assertIn("base ref moved", result.stderr)
        self.assertFalse((self.capture / "args").exists())
        worktrees = self.git_output("worktree", "list", "--porcelain")
        self.assertEqual(worktrees.count("worktree "), 1)

    def test_reports_an_unsupported_codex_cli_before_creating_a_worktree(self):
        result = subprocess.run(
            self.adapter_command(),
            input="Review this change.\n",
            env=self.adapter_env(FAKE_CODEX_HELP_STATUS="1"),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 69)
        self.assertIn("codex exec review is not supported", result.stderr)
        self.assertFalse((self.capture / "args").exists())
        worktrees = self.git_output("worktree", "list", "--porcelain")
        self.assertEqual(worktrees.count("worktree "), 1)

    def test_cleans_up_the_temporary_worktree_when_review_fails(self):
        result = subprocess.run(
            self.adapter_command(),
            input="Review this change.\n",
            env=self.adapter_env(FAKE_CODEX_RUN_STATUS="42"),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 42)
        self.assertTrue((self.capture / "args").exists())
        worktrees = self.git_output("worktree", "list", "--porcelain")
        self.assertEqual(worktrees.count("worktree "), 1)


if __name__ == "__main__":
    unittest.main()
