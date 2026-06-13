# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/code-style-contracts` for style, config, schema, naming, validation, or comment-sensitive edits.
- Use TodoWrite only when style cleanup spans multiple files or gates.
- Prefer the repository formatter, linter, type checker, and smallest relevant tests over runtime-specific heuristics.
- Ask inline or use AskUserQuestion only when a contract change has real alternatives.
- Do not duplicate or weaken the workflow and stop conditions in `SKILL.md`.
