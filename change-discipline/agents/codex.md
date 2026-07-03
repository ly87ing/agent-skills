# Codex Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `$change-discipline` for boundary/interface/dependency reviews and for code, config, schema, serialized data, naming, or comment changes.
- Use `update_plan` only when the change or verification spans multiple steps.
- Edit with the repository's existing tools and run the smallest relevant verification after each behavioral change.
- Surface compatibility, migration, or blast-radius assumptions before changing public contracts or shared boundaries.
- Prefer file and line evidence in final review notes when available.
- Do not duplicate or weaken the hard gate, workflow, and stop conditions in `SKILL.md`.
