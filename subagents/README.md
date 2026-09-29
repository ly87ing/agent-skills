# Subagent definitions

Runtime-specific subagent definitions that assign a model and reasoning effort by kind of work.
The delegating agent keeps requirements, design, review, and judgement on the main session's
model; only well-specified implementation is handed down a tier.

- `claude/implementer.md` — Claude Code, `model: sonnet`, `effort: high`. It uses the family
  alias, so a new Sonnet release needs no edit. Built-in subagents (Explore, Plan,
  general-purpose) already inherit the main session's model, so no definition is needed for
  deep work.

Codex has no equivalent here: it has no family aliases, so a role file would pin a concrete model
name that goes stale with every model generation, and its main session already runs the coding
tier.

Descriptions say what each subagent is for and do not say "use proactively": delegation stays the
exception, and the description only decides where it goes.

Agent Manager does not install these yet. Copy a file into `~/.claude/agents/` (all projects) or a
project's `.claude/agents/` by hand.
