#!/usr/bin/env python3
"""Extract genuine user messages from local agent session data for mining.

Read-only. Scans Claude Code project transcripts and Codex session rollouts,
filters machine-injected content, and writes per-corpus text files plus a
stats summary to --out. Claude messages already present in the prompt history
(~/.claude/history.jsonl) are skipped so the output is the unmined delta.

Usage:
  python3 extract_user_messages.py --out /tmp/mined
  python3 extract_user_messages.py --out /tmp/mined --claude-dir ~/.claude --codex-dir ~/.codex

Stdlib only; Python 3.10+.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

MAX_MSG_CHARS = 3000
KNOWN_PREFIX_CHARS = 200


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()[:KNOWN_PREFIX_CHARS]


def load_known_prompts(history_path: str) -> set[str]:
    known: set[str] = set()
    if not os.path.exists(history_path):
        return known
    with open(history_path, errors="replace") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            display = norm(entry.get("display") or "")
            if display:
                known.add(display)
    return known


def iter_claude_user_texts(path: str):
    with open(path, errors="replace") as fh:
        for line in fh:
            if '"type":"user"' not in line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "user" or entry.get("isMeta"):
                continue
            user_type = entry.get("userType")
            if user_type and user_type != "external":
                continue
            content = (entry.get("message") or {}).get("content")
            texts = []
            if isinstance(content, str):
                texts = [content]
            elif isinstance(content, list):
                texts = [item.get("text", "") for item in content
                         if isinstance(item, dict) and item.get("type") == "text"]
            for text in texts:
                yield entry.get("timestamp", ""), text.strip()


def iter_codex_user_texts(path: str):
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = entry.get("payload") or {}
            texts = []
            if payload.get("type") == "message" and payload.get("role") == "user":
                for item in payload.get("content") or []:
                    text = item.get("text") or item.get("input_text") or ""
                    if text:
                        texts.append(text)
            elif entry.get("type") == "event_msg" and payload.get("type") == "user_message":
                if payload.get("message"):
                    texts.append(payload["message"])
            for text in texts:
                yield entry.get("timestamp", ""), text.strip()


def keep(text: str) -> bool:
    if not text:
        return False
    if text.startswith(("<local-command", "<command-", "<system-reminder", "Caveat:")):
        return False
    if text.startswith("<") or "data:image" in text[:120]:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--claude-dir", default=os.path.expanduser("~/.claude"))
    parser.add_argument("--codex-dir", default=os.path.expanduser("~/.codex"))
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)

    stats = {"claude_files": 0, "claude_msgs": 0, "claude_delta": 0,
             "codex_files": 0, "codex_msgs": 0, "interrupts": 0}
    known = load_known_prompts(os.path.join(args.claude_dir, "history.jsonl"))

    by_key: dict[str, list[str]] = {}
    for path in sorted(glob.glob(os.path.join(args.claude_dir, "projects", "*", "*.jsonl"))):
        stats["claude_files"] += 1
        project = os.path.basename(os.path.dirname(path))
        for timestamp, text in iter_claude_user_texts(path):
            if "[Request interrupted" in text[:60] and len(text) < 80:
                stats["interrupts"] += 1
                continue
            if not keep(text):
                continue
            stats["claude_msgs"] += 1
            if norm(text) in known:
                continue
            stats["claude_delta"] += 1
            snippet = text[:MAX_MSG_CHARS] + (" ...[TRUNC]" if len(text) > MAX_MSG_CHARS else "")
            by_key.setdefault(f"claude-delta-{project[-48:]}", []).append(
                f"[{timestamp[:16]}] ({os.path.basename(path)[:12]})\n{snippet}\n---")

    for path in sorted(glob.glob(os.path.join(args.codex_dir, "sessions", "**", "*.jsonl"),
                                 recursive=True)):
        stats["codex_files"] += 1
        seen_in_file: set[str] = set()
        for timestamp, text in iter_codex_user_texts(path):
            if not keep(text) or norm(text) in seen_in_file:
                continue
            seen_in_file.add(norm(text))
            stats["codex_msgs"] += 1
            snippet = text[:MAX_MSG_CHARS] + (" ...[TRUNC]" if len(text) > MAX_MSG_CHARS else "")
            by_key.setdefault(f"codex-{os.path.basename(path)[:40]}", []).append(
                f"[{timestamp[:16]}]\n{snippet}\n---")

    for key, items in by_key.items():
        out_path = os.path.join(args.out, f"{key}.txt")
        with open(out_path, "w") as fh:
            fh.write("\n".join(items))
        print(f"{len(items):5d} msgs  {out_path}")
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
