# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/frontend-verification` for UI, browser automation, interactive HTML, or frontend validation tasks.
- Use `/run` when Claude Code has a project launch recipe and the task needs live app proof.
- Use TodoWrite only when frontend validation has multiple routes, states, or artifacts.
- Keep any Claude dynamic context injection in project-local skills, not this portable core skill.
- Do not duplicate or weaken the browser, screenshot, and regression coverage rules in `SKILL.md`.
