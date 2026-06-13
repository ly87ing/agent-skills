# Codex Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `$code-style-contracts` for code, config, schema, serialized data, or comment changes.
- Use `update_plan` only when the cleanup or verification spans multiple steps.
- Edit with the repository's existing tools and run the smallest relevant verification after each behavioral change.
- Surface compatibility or migration assumptions before changing public contracts.
- Do not duplicate or weaken the workflow and stop conditions in `SKILL.md`.
