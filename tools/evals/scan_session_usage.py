#!/usr/bin/env python3
"""Count how often this catalog's skills load in real sessions on this machine.

The trigger runner asks a judge which single skill it would pick for a one-turn
request; real sessions are long, often open through another skill, and the model
decides mid-task whether to load anything at all. This script reads the local
transcripts both runtimes already keep and reports, per skill, how many sessions
loaded it, and — for sessions that edited a file — whether it loaded before the
first edit, only after it, or never. That last split is what an edit-time gate
such as `change-discipline` has to win.

Read-only, no model calls, stdlib only. It prints counts and nothing else: no
prompts, paths, or project names, so the output is safe to paste into docs.
Sessions whose working directory is a temporary directory (eval runs, probes) or
this repository (maintaining the catalog, where reading a SKILL.md is not using
it) are excluded and counted separately.

What counts as a load:
  Claude Code  a `Skill` tool call naming the skill, or a user-invoked
               `/skill` whose injected text starts "Base directory for this skill:"
  Codex        any tool call whose input names `skills/<skill>/SKILL.md`
What counts as an edit, outside temporary directories:
  Claude Code  Edit, Write, MultiEdit, NotebookEdit
  Codex        an apply_patch body (`*** Begin Patch`)

Usage:
  python3 tools/evals/scan_session_usage.py              # last 30 days
  python3 tools/evals/scan_session_usage.py --days 7
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
BASE_DIR_PREFIX = "Base directory for this skill:"
PATCH_TARGET = re.compile(r"\*\*\* (?:Update|Add|Delete) File: ([^\n\\]+)")


def temp_roots() -> tuple[str, ...]:
    roots = {"/tmp", "/private/tmp", "/var/folders", "/private/var/folders"}
    roots.add(os.path.realpath(tempfile.gettempdir()))
    return tuple(sorted(roots))


def is_under(path: str, roots: tuple[str, ...]) -> bool:
    return any(path == root or path.startswith(root.rstrip("/") + "/") for root in roots)


def catalog_skills(skills_dir: Path) -> list[str]:
    return sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md"))


class Session:
    """One transcript reduced to what the report needs: its cwd, the event index of
    each skill's first load, and the event index of the first edit."""

    def __init__(self) -> None:
        self.cwd = ""
        self.first_load: dict[str, int] = {}
        self.first_edit: int | None = None

    def load(self, skill: str, index: int) -> None:
        self.first_load.setdefault(skill, index)

    def edit(self, index: int) -> None:
        if self.first_edit is None:
            self.first_edit = index


def read_jsonl(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def parse_claude(path: Path, skills: list[str], temps: tuple[str, ...]) -> Session:
    session = Session()
    for index, entry in enumerate(read_jsonl(path)):
        if not isinstance(entry, dict):
            continue
        if not session.cwd and isinstance(entry.get("cwd"), str):
            session.cwd = entry["cwd"]
        message = entry.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and entry.get("type") == "user":
                text = block.get("text") or ""
                if text.startswith(BASE_DIR_PREFIX):
                    name = Path(text[len(BASE_DIR_PREFIX):].splitlines()[0].strip()).name
                    if name in skills:
                        session.load(name, index)
            if block.get("type") != "tool_use":
                continue
            tool_input = block.get("input") if isinstance(block.get("input"), dict) else {}
            if block.get("name") == "Skill" and tool_input.get("skill") in skills:
                session.load(tool_input["skill"], index)
            elif block.get("name") in EDIT_TOOLS:
                target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
                if target and not is_under(target, temps):
                    session.edit(index)
    return session


def parse_codex(path: Path, skills: list[str], temps: tuple[str, ...]) -> Session:
    session = Session()
    names = re.compile(r"skills/(" + "|".join(map(re.escape, skills)) + r")/SKILL\.md")
    for index, entry in enumerate(read_jsonl(path)):
        if not isinstance(entry, dict):
            continue
        payload = entry.get("payload") if isinstance(entry.get("payload"), dict) else {}
        if entry.get("type") == "session_meta" and isinstance(payload.get("cwd"), str):
            session.cwd = payload["cwd"]
        if payload.get("type") not in ("function_call", "custom_tool_call", "local_shell_call"):
            continue
        raw = payload.get("input") or payload.get("arguments") or payload.get("action") or ""
        text = raw if isinstance(raw, str) else json.dumps(raw)
        for match in names.finditer(text):
            session.load(match.group(1), index)
        if "*** Begin Patch" in text:
            targets = PATCH_TARGET.findall(text)
            if any(not is_under(t.strip(), temps) for t in targets) or not targets:
                session.edit(index)
    return session


def recent(paths, cutoff: float):
    return [p for p in paths if p.is_file() and p.stat().st_mtime >= cutoff]


def summarise(sessions: list[Session], skills: list[str], temps: tuple[str, ...]) -> dict:
    repo = str(REPO_ROOT)
    kept = [s for s in sessions if not is_under(s.cwd, temps) and not is_under(s.cwd, (repo,))]
    editing = [s for s in kept if s.first_edit is not None]
    rows = {}
    for skill in skills:
        before = sum(1 for s in editing if s.first_load.get(skill, 1 << 62) < s.first_edit)
        after = sum(1 for s in editing if skill in s.first_load) - before
        rows[skill] = {
            "loaded": sum(1 for s in kept if skill in s.first_load),
            "before_first_edit": before,
            "only_after": after,
            "never": len(editing) - before - after,
        }
    return {
        "sessions": len(kept),
        "excluded_temp": sum(1 for s in sessions if is_under(s.cwd, temps)),
        "excluded_repo": sum(1 for s in sessions if is_under(s.cwd, (repo,))),
        "editing": len(editing),
        "skills": rows,
    }


def render(runtime: str, summary: dict) -> str:
    lines = [
        f"{runtime}: {summary['sessions']} sessions "
        f"({summary['excluded_temp']} in temporary directories and "
        f"{summary['excluded_repo']} in this repository excluded); "
        f"{summary['editing']} edited a file",
        f"  {'skill':24} {'loaded':>7} {'before 1st edit':>16} {'only after':>11} {'never':>6}",
    ]
    for skill, row in summary["skills"].items():
        lines.append(
            f"  {skill:24} {row['loaded']:>7} {row['before_first_edit']:>16} "
            f"{row['only_after']:>11} {row['never']:>6}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--claude-root", type=Path, default=Path.home() / ".claude" / "projects")
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex" / "sessions")
    parser.add_argument("--skills-dir", type=Path, default=REPO_ROOT / "skills")
    args = parser.parse_args(argv)

    skills = catalog_skills(args.skills_dir)
    if not skills:
        print(f"no skills found under {args.skills_dir}", file=sys.stderr)
        return 1
    temps = temp_roots()
    cutoff = time.time() - args.days * 86400
    claude = [parse_claude(p, skills, temps) for p in recent(args.claude_root.glob("*/*.jsonl"), cutoff)]
    codex = [parse_codex(p, skills, temps) for p in recent(args.codex_root.rglob("*.jsonl"), cutoff)]
    print(f"last {args.days} days")
    print(render("claude-code", summarise(claude, skills, temps)))
    print(render("codex", summarise(codex, skills, temps)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
