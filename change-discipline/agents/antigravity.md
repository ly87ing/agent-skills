# Antigravity CLI Adapter

Core source of truth: `SKILL.md`.

- Invoke `change-discipline` explicitly for boundary/interface/dependency reviews and for style, config, schema, naming, validation, or comment-sensitive edits when Antigravity CLI exposes this plugin skill.
- Use Antigravity CLI's native planning or status surface only when the change or verification spans multiple steps.
- Prefer the repository formatter, linter, type checker, and smallest relevant tests over runtime-specific heuristics.
- Surface compatibility, migration, or blast-radius assumptions before changing public contracts or shared boundaries.
- Keep Antigravity CLI plugin rules separate from this portable core skill.
- Do not duplicate or weaken the hard gate, workflow, and stop conditions in `SKILL.md`.
