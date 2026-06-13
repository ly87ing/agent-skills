# Claude Code Adapter

Core source of truth: `SKILL.md`.

- Invoke explicitly as `/architecture-change-review` when needed.
- Use TodoWrite only when the review becomes a multi-step execution track.
- Ask inline or use AskUserQuestion for concrete choices only; do not turn routine review checks into user prompts.
- Do not add Claude-specific frontmatter or tool grants to `SKILL.md`; keep runtime packaging derived from this adapter.
- Do not duplicate or weaken the workflow and stop conditions in `SKILL.md`.
