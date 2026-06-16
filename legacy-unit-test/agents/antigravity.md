# Antigravity CLI Adapter

Core source of truth: `SKILL.md`.

- Invoke `legacy-unit-test` explicitly in Antigravity CLI for legacy repositories that need meaningful unit-test seeding before refactoring.
- Use Antigravity CLI's native planning or status surface only when baseline discovery, risk mapping, test writing, and verification are distinct phases.
- Keep each batch scoped to 1 to 3 High Priority modules, with visible test command results, coverage output, and testing-doc updates.
- Stop for approval before dependencies, CI, build scripts, production-code seams, public API changes, schema changes, or runtime config changes.
- Treat customer coverage targets as parameters, not fixed values hardcoded into the skill or tests.
- Do not duplicate or weaken the behavior-preservation, meaningful-coverage, and stop-condition gates in `SKILL.md`.
