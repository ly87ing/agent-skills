from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest import mock


RUNNER_PATH = Path(__file__).with_name("run_trigger_evals.py")
RUNNER_SPEC = importlib.util.spec_from_file_location("run_trigger_evals", RUNNER_PATH)
assert RUNNER_SPEC is not None and RUNNER_SPEC.loader is not None
runner = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(runner)


class TriggerEvalHarnessTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
