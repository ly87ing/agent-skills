# Subagent definitions

Runtime-specific subagent definitions that assign a model and reasoning effort by kind of work.
The delegating agent keeps requirements, design, review, and judgement on the main session's
model; only well-specified implementation is handed down a tier.

- `claude/implementer.md` — Claude Code, `model: sonnet`, `effort: high`. It uses the family
  alias, so a new Sonnet release needs no edit.

Codex has no equivalent here: it has no family aliases, so a role file would pin a concrete model
name that goes stale with every model generation.

## Cost

A subagent given no model inherits the main session's. In one session with the main session on
Fable, six parallel `general-purpose` readers inherited Fable, and the plan's allowance ran out.
Set `CLAUDE_CODE_SUBAGENT_MODEL` to `opus` in `~/.claude/settings.json` under `env` so unassigned
subagents stop at Opus; a definition's `model` (such as `implementer`'s `sonnet`) and a model
passed on the call still win. The variable does not move the built-in `Explore` (main model,
capped at Opus) or `Plan` (main model), as the documentation says and one run with an Opus main
session confirmed for `Plan`. A fork always runs on the main session's model and ignores any
override, so the variable does not cap it either.

A fresh subagent shares no prompt cache with the main session, so it pays for everything it reads.
Hand a fresh subagent work that needs little context. When the work needs what the main session
already holds, continuing an existing subagent, or a fork (same model, same prefix, so the prefix
is read from cache), is cheaper than a new one re-reading it; on a Fable main session a fork is
Fable, so do the work in the main session instead.

Descriptions say what each subagent is for and do not say "use proactively": delegation stays the
exception, and the description only decides where it goes.

## Installing

Agent Manager does not install these yet. Copy a file into `~/.claude/agents/` (all projects) or a
project's `.claude/agents/` by hand.
