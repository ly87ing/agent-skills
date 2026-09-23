from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


RUNNER_PATH = Path(__file__).resolve().parents[1] / "tools" / "evals" / "run_codex_catalog_evals.py"
RUNNER_SPEC = importlib.util.spec_from_file_location("run_codex_catalog_evals", RUNNER_PATH)
assert RUNNER_SPEC is not None and RUNNER_SPEC.loader is not None
runner = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(runner)


class CodexCatalogEvalHarnessTests(unittest.TestCase):
    def test_auth_probe_reports_explicit_login_failure(self):
        completed = subprocess.CompletedProcess(
            ["codex", "login", "status"],
            1,
            "Not logged in\n",
            "",
        )
        with mock.patch.object(runner.subprocess, "run", return_value=completed) as run:
            problem = runner.codex_auth_problem()

        self.assertEqual(problem, "`codex` CLI is not authenticated; run `codex login`")
        self.assertIs(run.call_args.kwargs["stdin"], subprocess.DEVNULL)

    def test_runtime_inventory_ignores_non_runtime_and_cache_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = Path(temp_dir) / "demo"
            (skill / "references").mkdir(parents=True)
            (skill / "scripts" / "__pycache__").mkdir(parents=True)
            (skill / "evals").mkdir()
            (skill / "SKILL.md").write_text("instructions", encoding="utf-8")
            (skill / "references" / "guide.md").write_text("guide", encoding="utf-8")
            (skill / "scripts" / "__pycache__" / "tool.pyc").write_bytes(b"cache")
            (skill / "evals" / "evals.json").write_text("{}", encoding="utf-8")

            inventory = runner.runtime_inventory(skill)

        self.assertEqual(set(inventory), {"SKILL.md", "references/guide.md"})

    def test_matching_installed_skill_rejects_stale_runtime_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source" / "demo-skill"
            installed = root / "installed" / "demo-skill"
            source.mkdir(parents=True)
            installed.mkdir(parents=True)
            (source / "SKILL.md").write_text("current", encoding="utf-8")
            (installed / "SKILL.md").write_text("stale", encoding="utf-8")
            with mock.patch.object(runner, "ROOT", root / "source"):
                matched, _ = runner.matching_installed_skill(
                    "demo-skill",
                    [root / "installed"],
                )

        self.assertIsNone(matched)

    def test_run_process_kills_the_process_group_on_timeout(self):
        process = mock.Mock()
        process.pid = 4321
        process.communicate.side_effect = [
            subprocess.TimeoutExpired(["codex"], 1),
            ("", ""),
        ]

        with mock.patch.object(runner.subprocess, "Popen", return_value=process):
            with mock.patch.object(runner.os, "name", "posix"):
                with mock.patch.object(runner.os, "killpg") as killpg:
                    result = runner.run_process(["codex"], "/tmp")

        self.assertIsNone(result)
        killpg.assert_called_once_with(4321, runner.signal.SIGKILL)

    def test_run_codex_uses_fresh_read_only_directory_and_records_multiple_skills(self):
        calls: list[tuple[list[str], Path, object]] = []

        def fake_run(command: list[str], cwd: str):
            sandbox = Path(command[command.index("--cd") + 1])
            self.assertTrue(sandbox.is_dir())
            self.assertEqual(sandbox, Path(cwd))
            self.assertEqual(list(sandbox.iterdir()), [])
            calls.append((command, sandbox, subprocess.DEVNULL))
            events = [
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": (
                            "/bin/zsh -lc \"sed -n '1,200p' /tmp/skills/reader-facing-writing/SKILL.md "
                            "/tmp/skills/artifact-hygiene/SKILL.md\""
                        ),
                    },
                },
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": "final answer"},
                },
            ]
            return subprocess.CompletedProcess(
                command,
                0,
                "\n".join(json.dumps(event) for event in events),
                "",
            )

        with mock.patch.object(runner, "run_process", side_effect=fake_run):
            result = runner.run_codex("Review the artifact.")

        self.assertEqual(result["loaded"], ["reader-facing-writing", "artifact-hygiene"])
        self.assertEqual(result["response"], "final answer")
        command, sandbox, stdin = calls[0]
        self.assertIn("--ephemeral", command)
        self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
        self.assertIs(stdin, subprocess.DEVNULL)
        self.assertFalse(sandbox.exists())


if __name__ == "__main__":
    unittest.main()
