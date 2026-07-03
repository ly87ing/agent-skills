# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/change-discipline` for boundary/interface/dependency reviews and for code style, config, schema, naming, validation, or comment-sensitive edits.
- Use TodoWrite only when the change becomes a multi-step execution track spanning multiple files or gates.
- Prefer the repository formatter, linter, type checker, and smallest relevant tests over runtime-specific heuristics.
- Ask inline or use AskUserQuestion only when a contract or boundary change has real alternatives; do not turn routine checks into user prompts.
- Do not add Claude-specific frontmatter or tool grants to `SKILL.md`; keep runtime packaging derived from this adapter.
- Do not duplicate or weaken the hard gate, workflow, and stop conditions in `SKILL.md`.
