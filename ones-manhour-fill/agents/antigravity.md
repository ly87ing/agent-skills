# Antigravity CLI Adapter

Core source of truth: `SKILL.md`.

- Invoke `ones-manhour-fill` for ONES daily manhour backfill into a parent task's actual subtasks in Antigravity CLI.
- Map preflight, parent/subtask discovery, existing-record guard, write, and readback verification to Antigravity CLI's native planning or status surface when available.
- Use the available ONES connector or project profile for credential-safe API calls.
- Use `scripts/normalize_manhour_plan.py` for dry-run allocation checks before live writes.
- Do not duplicate or weaken the existing-record, add-only write, target-total, description-integrity, no-fabrication, and readback gates in `SKILL.md`.
