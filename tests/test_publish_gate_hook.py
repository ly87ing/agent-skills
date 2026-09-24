"""Guard the PreToolUse hook that enforces the last line of rules/core.md.

The hook is the gate the rule cannot be: a line in CLAUDE.md is context the model may
weigh, while a hook runs on every tool call. Its two failure modes are both silent. A
missed publishing shape lets a push through with no question asked, and a false positive
on an everyday command trains the user to click through the prompt. Both lists below are
the pinned shapes.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "rules" / "hooks" / "publish_gate.py"

PUBLISHING = [
    "git push",
    "git -C /repo push origin main",
    "FOO=1 git push",
    "cd repo && git push -u origin feature",
    'bash -c "cd repo && git push"',
    "echo $(git push origin main)",
    "x=`git push`",
    "git push origin main 2>&1 | tail -1",
    "/usr/bin/git push",
    "gh pr create --title x --body y",
    "gh pr merge 12 --squash",
    "gh release create v1.0",
    "gh api repos/o/r/pulls -f title=x",
    "gh api -X DELETE repos/o/r/git/refs/heads/x",
    "glab mr create --fill",
    "npm publish",
    "yarn npm publish",
    "docker push registry.example.com/app:1",
    "twine upload dist/*",
    "cargo publish",
    "./gradlew publish",
    "mvn deploy",
    "scp build.tgz deploy@web:/srv/",
    "rsync -a dist/ deploy@web:/srv/app",
    "curl -T report.pdf https://files.example.com/",
]

EVERYDAY = [
    "git status",
    "git log --grep push",
    "git commit -m 'push later'",
    'git commit -m "a; git push"',
    'echo "git push"',
    "git push --dry-run",
    "git push -n origin main",
    "gh pr view 12",
    "gh api repos/o/r",
    "npm test",
    "npm publish --dry-run",
    "docker build -t app .",
    "./gradlew publishToMavenLocal",
    "scp deploy@web:/srv/app.log .",
    "curl https://example.com/health",
]


def run_hook(payload) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )


def decision(payload) -> str | None:
    result = run_hook(payload)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    if not result.stdout.strip():
        return None
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse", output
    return output["permissionDecision"]


class PublishGateHookTests(unittest.TestCase):
    def test_publishing_commands_ask_first(self):
        for command in PUBLISHING:
            with self.subTest(command=command):
                self.assertEqual(decision({"tool_name": "Bash", "tool_input": {"command": command}}), "ask")

    def test_everyday_commands_pass_silently(self):
        for command in EVERYDAY:
            with self.subTest(command=command):
                self.assertIsNone(decision({"tool_name": "Bash", "tool_input": {"command": command}}))

    def test_mcp_tools_that_publish_ask_first(self):
        for tool in ("mcp__github__push_files", "mcp__github__create_pull_request",
                     "mcp__github__merge_pull_request", "mcp__slack__send_message"):
            with self.subTest(tool=tool):
                self.assertEqual(decision({"tool_name": tool, "tool_input": {}}), "ask")
        for tool in ("mcp__github__get_file_contents", "Read", "Edit"):
            with self.subTest(tool=tool):
                self.assertIsNone(decision({"tool_name": tool, "tool_input": {}}))

    def test_unreadable_payload_does_not_block(self):
        for payload in ("not json", "[]", ""):
            with self.subTest(payload=payload):
                result = run_hook(payload)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
