# Antigravity CLI Adapter

Core source of truth: `SKILL.md`.

- Invoke `code-style-contracts` explicitly for style, config, schema, naming, validation, or comment-sensitive edits in Antigravity CLI.
- Use Antigravity CLI's native planning or status surface only when cleanup or verification spans multiple steps.
- Prefer the repository formatter, linter, type checker, and smallest relevant tests over runtime-specific heuristics.
- Surface compatibility or migration assumptions before changing public contracts.
- Do not duplicate or weaken the workflow and stop conditions in `SKILL.md`.
