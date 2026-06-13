# Codex Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `$artifact-hygiene` before creating, retaining, or committing generated artifacts.
- Use `update_plan` only when cleanup has multiple visible steps.
- Prefer temporary directories for one-off traces, screenshots, reports, downloads, and scratch scripts.
- Re-check `git status --short --ignored` before finalizing artifact decisions.
- Do not duplicate or weaken the placement and cleanup rules in `SKILL.md`.
