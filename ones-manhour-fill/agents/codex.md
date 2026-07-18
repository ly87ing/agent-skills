# Codex Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `$ones-manhour-fill` for ONES daily manhour backfill into parent-task subtasks.
- Use the available ONES connector for credential-safe GraphQL/REST calls; never print token or user id values.
- Track preflight, parent/subtask discovery, existing-record guard, write, and readback verification with `update_plan` when the run spans multiple records.
- Use `scripts/normalize_manhour_plan.py` for dry-run allocation checks before live ONES writes.
- Do not duplicate or weaken the existing-record, add-only write, target-total, description-integrity, no-fabrication, and readback gates in `SKILL.md`.
