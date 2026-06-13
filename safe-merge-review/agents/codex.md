# Codex Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `$safe-merge-review` for merge execution or audit work.
- Map repo modeling, merge execution, conflict review, completeness proof, validation, and push decision to `update_plan`.
- Ask for approval before dirty-worktree handling or destructive git operations when policy requires it.
- Prefer non-interactive git commands and keep evidence in command output plus final summary.
- Do not duplicate or weaken the proof, semantic review, validation, and push gates in `SKILL.md`.
