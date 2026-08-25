from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


RUNNER_PATH = Path(__file__).with_name("run_behaviour_evals.py")
RUNNER_SPEC = importlib.util.spec_from_file_location("run_behaviour_evals", RUNNER_PATH)
assert RUNNER_SPEC is not None and RUNNER_SPEC.loader is not None
runner = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(runner)


class BehaviourEvalHarnessTests(unittest.TestCase):
    def test_auth_probe_reports_explicit_logged_out_state(self):
        completed = subprocess.CompletedProcess(
            ["claude", "auth", "status"],
            1,
            '{"loggedIn": false, "authMethod": "none"}\n',
            "",
        )
        with mock.patch.object(runner.subprocess, "run", return_value=completed):
            problem = runner.claude_auth_problem()

        self.assertEqual(
            problem,
            "`claude` CLI is not authenticated; run `claude auth login`",
        )

    def test_run_claude_disables_ambient_customizations_and_persistence(self):
        completed = subprocess.CompletedProcess([], 0, "OK\n", "")
        with mock.patch.object(runner.subprocess, "run", return_value=completed) as run:
            result = runner.run_claude(
                "Reply with OK.",
                "sonnet",
                1,
                cwd="/tmp/behaviour-eval-test",
                tools="",
            )

        self.assertEqual(result, "OK")
        command = run.call_args.args[0]
        for option in (
            "--safe-mode",
            "--disable-slash-commands",
            "--no-session-persistence",
            "--strict-mcp-config",
        ):
            self.assertIn(option, command)
        tools_index = command.index("--tools")
        self.assertEqual(command[tools_index + 1], "")

    def test_runtime_copy_includes_only_model_visible_skill_resources(self):
        with tempfile.TemporaryDirectory() as destination:
            runtime_skill = runner.materialize_runtime_skill(
                "safe-merge-review",
                Path(destination),
            )

            self.assertTrue((runtime_skill / "SKILL.md").is_file())
            self.assertTrue((runtime_skill / "references").is_dir())
            self.assertTrue((runtime_skill / "scripts").is_dir())
            for excluded in ("agents", "evals", "tests"):
                self.assertFalse((runtime_skill / excluded).exists())

    def test_answer_once_uses_fresh_directories_for_both_arms(self):
        calls: list[tuple[str, Path, set[str]]] = []

        def fake_run(
            prompt: str,
            model: str,
            timeout: int,
            cwd: str,
            tools: str = runner.READ_ONLY_TOOLS,
        ) -> str:
            sandbox = Path(cwd)
            calls.append((prompt, sandbox, {entry.name for entry in sandbox.iterdir()}))
            return "answer"

        with mock.patch.object(runner, "run_claude", side_effect=fake_run):
            answers = runner.answer_once(
                "safe-merge-review",
                "Use the bundled checklist.",
                "Review this merge.",
                "sonnet",
            )

        self.assertEqual(answers, {"with": "answer", "without": "answer"})
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0][1], calls[1][1])
        self.assertEqual(calls[0][2], {"safe-merge-review"})
        self.assertEqual(calls[1][2], set())
        self.assertIn(str(calls[0][1] / "safe-merge-review"), calls[0][0])
        for _, sandbox, _ in calls:
            self.assertFalse(sandbox.exists())


    def test_answer_once_can_compare_a_previous_skill_snapshot(self):
        calls: list[tuple[str, set[str], str | None]] = []

        def fake_run(
            prompt: str,
            model: str,
            timeout: int,
            cwd: str,
            tools: str = runner.READ_ONLY_TOOLS,
        ) -> str:
            sandbox = Path(cwd)
            reference = sandbox / "safe-merge-review" / "references" / "old.md"
            calls.append(
                (
                    prompt,
                    {entry.name for entry in sandbox.iterdir()},
                    reference.read_text(encoding="utf-8") if reference.exists() else None,
                )
            )
            return "answer"

        with tempfile.TemporaryDirectory() as baseline:
            baseline_skill = Path(baseline) / "safe-merge-review"
            (baseline_skill / "references").mkdir(parents=True)
            (baseline_skill / "SKILL.md").write_text(
                "---\nname: safe-merge-review\ndescription: baseline\n---\nUse the old checklist.\n",
                encoding="utf-8",
            )
            (baseline_skill / "references" / "old.md").write_text(
                "old reference",
                encoding="utf-8",
            )
            with mock.patch.object(runner, "run_claude", side_effect=fake_run):
                answers = runner.answer_once(
                    "safe-merge-review",
                    "Use the current checklist.",
                    "Review this merge.",
                    "sonnet",
                    baseline_root=Path(baseline),
                )

        self.assertEqual(answers, {"with": "answer", "without": "answer"})
        self.assertEqual(calls[0][1], {"safe-merge-review"})
        self.assertEqual(calls[1][1], {"safe-merge-review"})
        self.assertIn("Use the current checklist.", calls[0][0])
        self.assertIn("Use the old checklist.", calls[1][0])
        self.assertIsNone(calls[0][2])
        self.assertEqual(calls[1][2], "old reference")


if __name__ == "__main__":
    unittest.main()
