from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCANNER_PATH = Path(__file__).resolve().parents[1] / "tools" / "evals" / "scan_session_usage.py"
SCANNER_SPEC = importlib.util.spec_from_file_location("scan_session_usage", SCANNER_PATH)
assert SCANNER_SPEC is not None and SCANNER_SPEC.loader is not None
scanner = importlib.util.module_from_spec(SCANNER_SPEC)
SCANNER_SPEC.loader.exec_module(scanner)

SKILLS = ["change-discipline", "verification"]
TEMPS = ("/scratch",)


def skill_call(name: str) -> dict:
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}}


def edit_call(path: str) -> dict:
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Edit", "input": {"file_path": path}}]}}


def codex_call(text: str) -> dict:
    return {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "input": text}}


class SessionUsageScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name: str, entries: list[dict]) -> Path:
        path = self.root / name
        path.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")
        return path

    def claude(self, name: str, cwd: str, entries: list[dict]):
        header = {"type": "user", "cwd": cwd, "message": {"content": "task"}}
        return scanner.parse_claude(self.write(name, [header, *entries]), SKILLS, TEMPS)

    def test_claude_splits_editing_sessions_by_when_the_skill_loaded(self):
        sessions = [
            self.claude("before.jsonl", "/work/a", [skill_call("change-discipline"), edit_call("/work/a/x.py")]),
            self.claude("after.jsonl", "/work/b", [edit_call("/work/b/x.py"), skill_call("change-discipline")]),
            self.claude("never.jsonl", "/work/c", [edit_call("/work/c/x.py")]),
            self.claude("no-edit.jsonl", "/work/d", [skill_call("verification")]),
        ]
        summary = scanner.summarise(sessions, SKILLS, TEMPS)

        self.assertEqual(summary["sessions"], 4)
        self.assertEqual(summary["editing"], 3)
        self.assertEqual(
            summary["skills"]["change-discipline"],
            {"loaded": 2, "before_first_edit": 1, "only_after": 1, "never": 1},
        )
        self.assertEqual(summary["skills"]["verification"]["loaded"], 1)
        self.assertEqual(summary["skills"]["verification"]["never"], 3)

    def test_claude_counts_a_user_invoked_skill_and_ignores_scratch_edits(self):
        invoked = {"type": "user", "message": {"content": [
            {"type": "text", "text": "Base directory for this skill: /home/u/.claude/skills/verification\n\n# Verification"}]}}
        session = self.claude("invoked.jsonl", "/work/a", [invoked, edit_call("/scratch/probe.py")])

        self.assertIn("verification", session.first_load)
        self.assertIsNone(session.first_edit)

    def test_temporary_and_repository_sessions_are_excluded_and_counted(self):
        sessions = [
            self.claude("eval.jsonl", "/scratch/run-1", [skill_call("verification")]),
            self.claude("repo.jsonl", str(scanner.REPO_ROOT), [skill_call("verification")]),
            self.claude("work.jsonl", "/work/a", []),
        ]
        summary = scanner.summarise(sessions, SKILLS, TEMPS)

        self.assertEqual((summary["sessions"], summary["excluded_temp"], summary["excluded_repo"]), (1, 1, 1))
        self.assertEqual(summary["skills"]["verification"]["loaded"], 0)

    def test_codex_reads_skill_files_and_patch_targets_from_tool_input(self):
        meta = {"type": "session_meta", "payload": {"cwd": "/work/a"}}
        read = codex_call("tools.exec_command({cmd:\"sed -n '1,260p' /home/u/.codex/skills/change-discipline/SKILL.md\"})")
        scratch_patch = codex_call('const patch = "*** Begin Patch\\n*** Add File: /scratch/x.txt\\n+a\\n*** End Patch"')
        real_patch = codex_call('const patch = "*** Begin Patch\\n*** Update File: /work/a/x.py\\n@@\\n-a\\n+b\\n*** End Patch"')
        session = scanner.parse_codex(self.write("codex.jsonl", [meta, read, scratch_patch, real_patch]), SKILLS, TEMPS)

        self.assertEqual(session.cwd, "/work/a")
        self.assertEqual(session.first_load, {"change-discipline": 1})
        self.assertEqual(session.first_edit, 3)

    def test_report_carries_counts_but_no_paths(self):
        sessions = [self.claude("before.jsonl", "/work/secret-project", [skill_call("change-discipline")])]
        report = scanner.render("claude-code", scanner.summarise(sessions, SKILLS, TEMPS))

        self.assertIn("change-discipline", report)
        self.assertNotIn("/work", report)
        self.assertNotIn("secret-project", report)


if __name__ == "__main__":
    unittest.main()
