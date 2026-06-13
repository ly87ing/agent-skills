# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/safe-merge-review <source-ref>` for merge execution or audit work.
- Map repo modeling, merge execution, conflict review, completeness proof, validation, and push decision to TodoWrite.
- Use AskUserQuestion only before dirty-worktree handling or destructive git operations.
- Do not grant broad `allowed-tools` in the portable core; Claude-only packaging may derive narrow git tool permissions from this adapter.
- Do not duplicate or weaken the proof, semantic review, validation, and push gates in `SKILL.md`.
