# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/session-mining` for harvest runs over local memory and session data.
- Fan out corpus slices to read-only subagents (Explore or general-purpose); apply their findings yourself and verify no subagent wrote or pushed anything.
- Run `scripts/extract_user_messages.py` via the shell tool; do not paste transcript files into context.
- Claude-side sources additionally include the auto-memory directories listed in `references/data-sources.md`.
- Do not duplicate or weaken the coverage, dedupe, and consent rules in `SKILL.md`.
