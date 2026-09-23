# Always-on rules

`core.md` is the always-on rule layer shared by Claude Code and Codex: the text that ends up in
`~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. It lives next to the skills because the two layers
are designed together — the rules carry only universal invariants, and everything conditional is a
skill that its description triggers.

## How it reaches a machine

Agent Manager reads every `rules/*.md` file except this README as a rule template when this
repository is one of its skill sources (a git mirror it fetches, or a local checkout it links).
Nothing is written anywhere until the user applies a template to an agent's rules file, and the
user sees the difference against the current file first. Editing `core.md` therefore changes no
machine by itself; after the change is pushed, "update source" in Agent Manager fetches it and
offers the new version, and a local-checkout source shows it immediately.

A new `.md` file in this directory becomes a new template in Agent Manager. `evals/` holds the
behaviour eval cases for `core.md`.

This directory moved here from the `agent-manager` repository (`agent-rule/rules`) on 2026-09-23
with its history; the measurement notes behind the decisions below are in that history. The merge
keeps the old paths, so read it with `git log 001ae92^2 -- src/shared/core.md` rather than
`git log --follow rules/core.md`.

## What belongs in core.md

Every line is paid for in every turn of every session, so it holds only two kinds of content:
universal invariants, and nothing else that a skill or memory could carry instead.

- **Invariant or procedure.** A fact that must hold in every turn stays; a workflow, checklist or
  when-X-do-Y habit goes to the skill that owns it, or to memory.
- **The delete test decides.** A line earns its slot only if removing it makes the agent go wrong.
  The test has two moving subjects — which runtime and model, and as of when — so a past pass
  expires; re-measure rather than trust an old result.
- **No skill routing lines.** They were removed on 2026-09-21: descriptions already sit in both
  runtimes' system prompts and trigger on their own (measured in isolated HOMEs without the lines,
  then re-checked on real Claude Code and Codex runtimes; see the main README). A routing line is a
  second copy of the trigger that couples this layer to skill names. Adding, splitting or renaming a
  skill must not require touching `core.md`.
- **No tool nudging.** No clauses that push the agent toward a particular MCP server or tool; tools
  are exposed automatically, and nudges have inflated context before.
- **No comments.** Claude Code strips HTML comments before injection, but Codex does not and bills
  them every turn, and any agent that opens the file with a read tool sees them anyway. Notes for
  maintainers go in this README.
- **Portable wording.** The same file goes to both runtimes; do not name one runtime's tool.

## Size budget

`tests/test_rule_contracts.py` caps `round(len(core.md) / 4)` at 545. The core has long run close
to the cap, so rewrites should be character-neutral or shorter. Raise the cap only together with a
line that passed the delete test, and lower it again when that line leaves; never raise it to make
the test pass. The same test checks that every eval anchor matches exactly one line.

## Measuring a line

`python3 tests/run_rule_behaviour_evals.py --rule <id>` runs each case twice — with `core.md` as it
stands and with the line under test removed — and grades both answers; the difference is the only
figure that justifies the line. It calls the model, so run it deliberately, not in CI.

- **Isolation is required.** The rules are already installed in the real `~/.claude/CLAUDE.md`, so a
  plain `claude -p` reads them in both arms. `--system-prompt` does not keep `CLAUDE.md` out and
  `--bare` cannot log in; the runner uses a throwaway HOME with only what auth needs, writes each
  arm's rules into it, and passes `--strict-mcp-config` so arms do not start the machine's MCP
  servers (rules about which tool to use cannot be measured this way).
- **Both arms carry the skill catalog.** Real sessions always have the descriptions in the system
  prompt; a line with lift against a bare model can be redundant next to a skill that claims the
  same ground. `--no-skills` reproduces the old bare arm; the two modes are not comparable.
- **Claude only.** No lift on Claude Code does not mean a line can go: Codex may still depend on it,
  unless the mechanism replacing it exists on both runtimes.
- **Anchors.** Cases live in `evals/core.json`; each rule's `anchor` must match exactly one line of
  `core.md`. Update the anchor when rewording the line.
- **Reading results.** Use the reading rules in the main README: judge with sonnet or larger, run
  enough repetitions, and compare Wilson intervals rather than point rates.
