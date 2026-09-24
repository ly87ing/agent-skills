#!/usr/bin/env python3
"""Claude Code PreToolUse hook: ask the user before any call that publishes work.

The last line of rules/core.md says never to publish, package, export, or send work
without explicit consent. A rule in CLAUDE.md is context, not enforcement; this hook is
the gate. It reads the hook payload on stdin and, when the call would push, publish,
release, merge, or upload, prints a `permissionDecision: "ask"` so Claude Code puts the
call in front of the user (under `claude -p` there is nobody to ask and the call is
denied). Every other call gets no output and proceeds. A payload it cannot read is let
through rather than blocking every tool call on a hook fault.

Standard library only. Registration is in rules/README.md.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys

OPERATOR_CHARS = set("();<>|&")
WRAPPERS = {"sudo", "env", "command", "exec", "time", "nohup", "xargs"}
SHELLS = {"bash", "sh", "zsh", "dash"}
GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}

SUBCOMMANDS = {
    "gh": {("pr", "create"), ("pr", "merge"), ("release", "create"), ("release", "upload"),
           ("gist", "create"), ("repo", "create")},
    "glab": {("mr", "create"), ("mr", "merge"), ("release", "create")},
}
PUBLISH_VERBS = {
    "npm": {"publish"}, "pnpm": {"publish"}, "yarn": {"publish"}, "twine": {"upload"},
    "poetry": {"publish"}, "cargo": {"publish"}, "gem": {"push"}, "docker": {"push"},
    "podman": {"push"}, "helm": {"push"}, "mvn": {"deploy"},
}
REMOTE_PATH = re.compile(r"^(?:[\w.-]+@)?[\w.-]+:(?!//)")
MCP_PUBLISH = re.compile(
    r"(?:^|_)(?:push|publish|merge|release|send|upload)(?:_|$)|create_pull_request|create_or_update_file"
)


def segments(command: str) -> list[list[str]]:
    """Split a shell command into simple commands, keeping quoted strings whole."""
    lexer = shlex.shlex(command.replace("`", " ; ").replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        tokens = command.replace("`", " ; ").split()
    result, current = [], []
    for token in tokens:
        if token and set(token) <= OPERATOR_CHARS:
            if current:
                result.append(current)
            current = []
        else:
            current.append(token)
    if current:
        result.append(current)
    return result


def program_and_args(tokens: list[str]) -> tuple[str, list[str]]:
    index = 0
    while index < len(tokens) and (tokens[index] in WRAPPERS or re.fullmatch(r"\w+=.*", tokens[index])):
        index += 1
    if index >= len(tokens):
        return "", []
    return os.path.basename(tokens[index]), tokens[index + 1:]


def git_subcommand(args: list[str]) -> str:
    index = 0
    while index < len(args) and args[index].startswith("-"):
        index += 2 if args[index] in GIT_OPTIONS_WITH_VALUE else 1
    return args[index] if index < len(args) else ""


def publishing_call(tokens: list[str], depth: int = 0) -> str | None:
    program, args = program_and_args(tokens)
    positional = [arg for arg in args if not arg.startswith("-")]
    if program in SHELLS and "-c" in args and depth < 3:
        inner = args[args.index("-c") + 1:]
        return publishing_command(inner[0], depth + 1) if inner else None
    if "--dry-run" in args:
        return None
    if program == "git" and git_subcommand(args) == "push":
        return None if "-n" in args else "git push"
    if program in SUBCOMMANDS and tuple(positional[:2]) in SUBCOMMANDS[program]:
        return f"{program} {' '.join(positional[:2])}"
    if program == "gh" and positional[:1] == ["api"]:
        method = next((args[i + 1] for i, a in enumerate(args[:-1]) if a in {"-X", "--method"}), "GET")
        if method.upper() != "GET" or any(a in {"-f", "-F", "--field", "--raw-field", "--input"} for a in args):
            return "gh api write"
    if program in PUBLISH_VERBS and PUBLISH_VERBS[program] & set(positional[:2]):
        return f"{program} {' '.join(positional[:2])}"
    if program in {"gradle", "gradlew"} and any(
        arg.startswith("publish") and arg != "publishToMavenLocal" for arg in positional
    ):
        return f"{program} publish"
    if program in {"scp", "rsync"} and positional and REMOTE_PATH.match(positional[-1]):
        return f"{program} to a remote host"
    if program == "curl" and any(arg in {"-T", "--upload-file"} for arg in args):
        return "curl upload"
    return None


def publishing_command(command: str, depth: int = 0) -> str | None:
    for tokens in segments(command):
        found = publishing_call(tokens, depth)
        if found:
            return found
    return None


def decide(payload: dict) -> str | None:
    tool = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input") or {}
    if tool == "Bash":
        return publishing_command(str(tool_input.get("command", "")))
    if tool.startswith("mcp__") and MCP_PUBLISH.search(tool.rsplit("__", 1)[-1]):
        return tool
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0
    found = decide(payload)
    if found:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    f"This call publishes work ({found}). The always-on rules require the "
                    "user's explicit consent first."
                ),
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
