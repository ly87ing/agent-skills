# Antigravity CLI Adapter

Core source of truth: `SKILL.md`.

- Invoke `artifact-hygiene` explicitly before keeping debug or generated files in Antigravity CLI work.
- Use Antigravity CLI's native planning or status surface only when cleanup spans multiple visible steps.
- Prefer shell checks such as `git status --short --ignored` when deciding whether an artifact can be committed.
- Keep disposable outputs outside the project unless the user asks for a durable artifact.
- Do not duplicate or weaken the placement and cleanup rules in `SKILL.md`.
