from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import unittest
from pathlib import Path
from unittest import mock


EVALS_DIR = Path(__file__).resolve().parents[1] / "tools" / "evals"
RUNNER_PATH = EVALS_DIR / "run_trigger_evals.py"
RUNNER_SPEC = importlib.util.spec_from_file_location("run_trigger_evals", RUNNER_PATH)
assert RUNNER_SPEC is not None and RUNNER_SPEC.loader is not None
runner = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(runner)


class TriggerEvalHarnessTests(unittest.TestCase):
    def test_auth_probe_reports_explicit_logged_out_state(self):
        completed = subprocess.CompletedProcess(
            ["claude", "auth", "status"],
            1,
            '{"loggedIn": false, "authMethod": "none"}\n',
            "",
        )
        with mock.patch.object(runner.subprocess, "run", return_value=completed) as run:
            problem = runner.claude_auth_problem()

        self.assertEqual(
            problem,
            "`claude` CLI is not authenticated; run `claude auth login`",
        )
        self.assertIs(run.call_args.kwargs["stdin"], subprocess.DEVNULL)

    def test_auth_probe_defers_to_normal_execution_for_unknown_cli_output(self):
        completed = subprocess.CompletedProcess(
            ["claude", "auth", "status"],
            1,
            "",
            "unknown command: auth",
        )
        with mock.patch.object(runner.subprocess, "run", return_value=completed):
            problem = runner.claude_auth_problem()

        self.assertIsNone(problem)

    def test_judge_runs_in_fresh_empty_directory_without_ambient_context(self):
        calls: list[tuple[list[str], Path, object]] = []

        def fake_run(command: list[str], **kwargs):
            sandbox = Path(kwargs["cwd"])
            self.assertTrue(sandbox.is_dir())
            self.assertEqual(list(sandbox.iterdir()), [])
            calls.append((command, sandbox, kwargs["stdin"]))
            return subprocess.CompletedProcess(command, 0, "target-skill\n", "")

        with mock.patch.object(runner.subprocess, "run", side_effect=fake_run):
            result = runner.judge(
                "- target-skill: does the target task",
                {"target-skill": "does the target task"},
                "sonnet",
                {"prompt": "Do the target task."},
            )

        self.assertEqual(result, "target-skill")
        self.assertEqual(len(calls), 1)
        command, sandbox, stdin = calls[0]
        for option in (
            "--safe-mode",
            "--disable-slash-commands",
            "--no-session-persistence",
            "--strict-mcp-config",
        ):
            self.assertIn(option, command)
        tools_index = command.index("--tools")
        self.assertEqual(command[tools_index + 1], "")
        self.assertIs(stdin, subprocess.DEVNULL)
        self.assertFalse(sandbox.exists())


class CatalogDisclosureTests(unittest.TestCase):
    """A run that saw only our own skills must not look like a run that saw everything.

    Both produce the same PASS/FAIL lines, so without an explicit warning an optimistic
    measurement is indistinguishable from a real one — which is how a green scored against
    a missing competitor once got recorded as a settled boundary.
    """

    def _run_main(self, argv: list[str]) -> tuple[int, str]:
        # An unmatched id makes main exit right after the catalog is announced,
        # so no judge call is ever made.
        stderr = io.StringIO()
        with mock.patch("sys.argv", ["run_trigger_evals.py", *argv]):
            with mock.patch.object(runner.shutil, "which", return_value="/usr/bin/claude"):
                with contextlib.redirect_stderr(stderr):
                    code = runner.main()
        return code, stderr.getvalue()

    def test_run_without_catalog_dir_warns_that_a_green_may_mean_a_missing_competitor(self):
        code, err = self._run_main(["--skill", "reader-facing-writing", "--ids", "99999"])

        self.assertEqual(code, 1)
        self.assertIn("no --catalog-dir", err)
        self.assertIn("CANNOT establish a boundary", err)

    def test_supplied_catalog_reports_its_capture_version_so_staleness_is_visible(self):
        fixtures = EVALS_DIR / "fixtures" / "builtin-skills"
        self.assertTrue((fixtures / "CAPTURED").exists(), "fixture must state what it was captured from")

        code, err = self._run_main(
            ["--skill", "reader-facing-writing", "--ids", "99999", "--catalog-dir", str(fixtures)]
        )

        self.assertEqual(code, 1)
        self.assertIn("neighbour skills", err)
        self.assertIn("Claude Code", err)
        self.assertNotIn("no --catalog-dir", err)

    def test_required_catalog_skill_prevents_an_incomplete_run(self):
        fixtures = EVALS_DIR / "fixtures" / "builtin-skills"

        code, err = self._run_main(
            [
                "--skill",
                "reader-facing-writing",
                "--ids",
                "99999",
                "--catalog-dir",
                str(fixtures),
                "--require-catalog-skill",
                "visualize",
            ]
        )

        self.assertEqual(code, 1)
        self.assertIn("required catalog skill(s) missing: visualize", err)


if __name__ == "__main__":
    unittest.main()
