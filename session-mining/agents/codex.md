# Codex Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `$session-mining` for harvest runs over local memory and session data.
- Use `update_plan` only when a run spans inventory, extraction, mining, and landing as separate visible phases.
- Run `scripts/extract_user_messages.py` in the sandbox shell; request read access to `~/.claude` and `~/.codex` if the sandbox blocks them.
- Codex-side sources include session rollouts and, when the memories feature is enabled, the automatic memory store (see `references/data-sources.md`).
- Do not duplicate or weaken the coverage, dedupe, and consent rules in `SKILL.md`.
