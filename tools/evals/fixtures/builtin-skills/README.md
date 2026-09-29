# Built-in skill descriptions, captured for the trigger-eval catalog

`run_trigger_evals.py` shows the judge only skills it can read from disk. A runtime's built-in
skills are compiled into its CLI and have no directory anywhere, so without this fixture the judge
never sees the neighbours that actually take our cases — and every competitive measurement reads
optimistically. That gap is what let a haiku-manufactured red on case #4 stand for weeks as a
documented boundary against a built-in dataviz skill the judge could never have been shown.

Each directory here holds a `SKILL.md` carrying nothing but the frontmatter the host puts in front
of the model. There is no body and there never should be: this is catalog metadata for a judge, not
a skill anyone loads.

Use it alongside the runtimes whose built-ins *are* on disk:

    python3 tools/evals/run_trigger_evals.py \
      --catalog-dir tools/evals/fixtures/builtin-skills \
      --catalog-dir ~/.codex/skills/.system \
      --model sonnet --runs-per-query 9

Codex keeps its six built-ins in `~/.codex/skills/.system` with valid frontmatter, so they need no
fixture — pass that path directly. The path is per-machine and deliberately not hardcoded in any
test.

## Provenance, and why it expires

Captured 2026-09-23 from the skill catalog a live Claude Code session renders into its system
prompt, on **Claude Code 2.1.281**. That is the only place these strings exist in readable form.
The strings are Anthropic's, reproduced only so the judge sees the real catalog; the repository's MIT license does not cover them.

They will drift as the CLI ships new versions, and a stale fixture is a new source of exactly the
false confidence it was built to remove. Re-capture whenever the CLI version changes, and record the
version above. A minor-version rule was too loose: between 2.1.220 and 2.1.281, the same minor
version, the rendered catalog gained `artifact-diagramming`, `code-review`, and `workflow-authoring`,
lost `review`, and changed three descriptions — `artifact-diagramming` being a direct competitor of
technical-diagramming. If you cannot confirm the capture is current, say the measurement was run
against a dated catalog rather than presenting it as the live one.

Descriptions are reproduced verbatim, including quirks (`claude-api`'s TRIGGER/SKIP block is folded
to one line because frontmatter is line-oriented, with no wording changed).
