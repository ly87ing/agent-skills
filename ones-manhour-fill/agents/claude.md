# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/ones-manhour-fill <date> <parent-task>` for ONES daily manhour backfill.
- Map preflight, parent/subtask discovery, existing-record guard, write, and readback verification to TodoWrite when the run spans multiple records.
- Use AskUserQuestion only for concrete conflicts such as identity mismatch, ambiguous parent task, existing overfill, non-additive correction, or a partial/non-work day where the screened real work cannot fill the target.
- Use `scripts/normalize_manhour_plan.py` for dry-run allocation checks and never expose ONES credentials through dynamic context injection.
- Do not duplicate or weaken the existing-record, add-only write, target-total, description-integrity, no-fabrication, and readback gates in `SKILL.md`.
