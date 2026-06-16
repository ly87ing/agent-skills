# Codex Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `$legacy-unit-test` for legacy repositories that need meaningful unit-test seeding before refactoring.
- Use `/goal` only for a small batch condition with visible evidence: changed files, test commands, exit codes, coverage output, and updated testing docs.
- Keep the goal scoped to 1 to 3 High Priority modules, not a whole-repository coverage chase.
- Stop for approval before dependencies, CI, build scripts, production-code seams, public API changes, schema changes, or runtime config changes.
- Use progress tracking only when baseline discovery, risk mapping, test writing, and verification are separate steps.
- Do not duplicate or weaken the behavior-preservation, meaningful-coverage, and stop-condition gates in `SKILL.md`.
