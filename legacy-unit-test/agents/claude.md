# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/legacy-unit-test` for legacy repositories that need meaningful characterization tests before refactoring.
- Use `/goal` only for a verifiable batch condition: 1 to 3 High Priority modules, no production-code changes, real assertions, test and coverage results, and updated testing docs.
- Do not use a vague goal such as raising coverage to the target; require transcript-visible evidence for each batch.
- Stop for approval before dependencies, CI, build scripts, production-code seams, public API changes, schema changes, or runtime config changes.
- Use Claude Code planning or task tracking only when discovery, target selection, implementation, and verification are distinct phases.
- Do not duplicate or weaken the behavior-preservation, meaningful-coverage, and stop-condition gates in `SKILL.md`.
