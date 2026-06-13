# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/artifact-hygiene` before keeping debug or generated files.
- Use TodoWrite only when artifact cleanup is part of a broader multi-step task.
- Prefer shell checks such as `git status --short --ignored` when deciding whether an artifact can be committed.
- Keep disposable outputs outside the project unless the user asks for a durable artifact.
- Do not duplicate or weaken the placement and cleanup rules in `SKILL.md`.
