# agent-skills

An open-source collection of general-purpose skills for agent runtimes such as Codex, Claude Code, and Antigravity CLI, with an emphasis on natural-language triggering, closed-loop workflows, verifiable evidence, and reusable resources.

## Project Scope

This repository collects directly reusable `SKILL.md` packages, not scattered prompts.

The goal is to distill high-frequency, error-prone engineering workflows that require reliable execution into team-reusable skills:

- with clear trigger conditions
- with minimal context requirements
- with an executable workflow
- with verification and failure boundaries
- with `references/` and `scripts/` that can be pushed down into shared resources

If a skill can only answer "how to do it" but cannot reliably get the task done, verified, and reported, that kind of content does not fit this repository's intended form.

## Current Catalog

| Skill | Description |
| --- | --- |
| [safe-merge-review](./safe-merge-review/SKILL.md) | Treats "merge succeeded" and "merge is correct" as separate concerns, emphasizing diff modeling, hotspot-overlap review, completeness verification, and the push decision; ships with triggering evals. |
| [change-discipline](./change-discipline/SKILL.md) | Disciplined changes to existing code: one pre-change hard gate (establish why current behavior exists, symptom-is-not-spec, blast radius, smallest verification) plus two facets — boundary/architecture review and code style/contract/naming/validation/comment constraints; ships with triggering evals. |
| [frontend-verification](./frontend-verification/SKILL.md) | Handles UI, browser automation, interactive HTML, responsive states, and frontend verification tool selection; ships with triggering evals. |
| [artifact-hygiene](./artifact-hygiene/SKILL.md) | Decides the placement and cleanup boundaries for generated files, debug artifacts, Playwright evidence, downloads, and temporary scripts; ships with triggering evals. |
| [reader-facing-writing](./reader-facing-writing/SKILL.md) | Writes or revises reader-facing plans, reports, proposals, specs, checklists, Markdown, and HTML documents; ships with triggering evals. |

All five skills are self-contained and have no cross-skill prerequisites.

## Design Principles

- Evidence first: do not reach conclusions by guessing; the verification method and result must be stated.
- Closed loop first: form a complete path from trigger, context, execution, and verification through to reporting.
- Sharing first: reusable rules should be pushed down into a shared layer, not scattered across page patches or ad hoc notes.
- Connector-first with a self-contained fallback: when a project ships a dedicated connector for an external system (issue tracker, CI, cloud), prefer it as the single source of truth; embedded raw HTTP or script templates are a documented fallback for runtimes without that connector, not a parallel source of truth. Because progressive loading does not cross skill boundaries, sibling skills cannot share one reference file, so the connector — not a shared file — is the point where that plumbing is deduplicated.
- Tool-neutral: enforce real observation of effects, but do not hard-bind to any one specific tool.
- Project-neutral: skills do not hardcode a single project's absolute paths, repo names, branches, internal UUIDs, or credential locations; project-specific information is injected via a discoverable project profile (resolved on demand or by asking the user), so the same skill can be reused across projects.
- Clear safety boundaries: spell out when it is okay to act automatically and when you must stop and escalate.
- Progressive loading: keep `SKILL.md` concise, push details down into `references/`, and push fragile steps into `scripts/` where possible.

## Repository Structure

```text
agent-skills/
├── safe-merge-review/
│   ├── SKILL.md                        # runtime-neutral source
│   ├── agents/
│   │   └── openai.yaml                 # Codex/OpenAI UI metadata
│   ├── evals/
│   ├── references/
│   ├── scripts/
│   └── tests/
├── change-discipline/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/
│   └── references/
├── frontend-verification/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/
│   └── references/
├── artifact-hygiene/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── evals/
└── reader-facing-writing/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── evals/
    └── references/
```

The top-level skill directories are the single source of truth, and the only content layer this repository maintains publicly.

Each canonical skill directory should be as self-contained as possible, typically including:

- `SKILL.md`: cross-runtime trigger conditions and the main workflow, kept open-standard and runtime-neutral
- `agents/openai.yaml`: Codex/OpenAI UI metadata and default invocation hints — the only file in `agents/`, because it is the only one a runtime actually reads
- `references/`: reference material loaded on demand (when a single file exceeds 100 lines, put a table of contents at the top so a partial read still conveys the full picture)
- `scripts/`: fragile steps suitable for distilling into deterministic helpers
- `evals/evals.json`: triggering and behavioral evaluation cases, with positive cases covering the triggering scenarios in `description`, and negative cases guarding against false triggers or confirming routing to a sibling skill. Eval prompts may be written in the primary user's language (including Chinese) to test real trigger phrasing — as may the optional `behaviour_prompt` that restates one of them with its material inlined for the behaviour runner; every other field stays English.
- `tests/`: per-skill unit tests guarding fragile script logic, run automatically by the top-level suite

All 5 current skills already ship with `evals/evals.json`, aligning with Anthropic's "evals first" skill authoring practice.

Verification commands:

- `python3 -m unittest discover -s tests` — structure/contract gate plus every per-skill unit suite
- `npx skills-ref validate ./<skill>` — the Agent Skills reference validator, run per skill; optional because it needs the network, while the suite above stays offline and stdlib-only
- `python3 tests/run_trigger_evals.py --model haiku` — judge each eval's triggering decision against a live model via `claude -p`; every call uses a fresh empty directory with ambient Claude customizations, skills, MCP servers, tools, and session persistence disabled (repeat with `--model sonnet` / `--model opus` to cover the multi-model checklist)
- `python3 tests/run_behaviour_evals.py --skill <name> --ids <id>` — measure whether the skill changes what the model does, against the same request run without it. For an existing-skill edit, pass an unpacked pre-edit catalog with `--baseline-root <path>` so the comparison arm uses the previous skill instead of no skill. Every answer and grading call gets a fresh temporary directory, disables ambient Claude customizations and session persistence, and receives no eval answers; a skill arm gets only a runtime copy of `SKILL.md`, `references/`, `scripts/`, and `assets/`, with read-only tools available for on-demand loading. It costs 4 model calls per case per run, so start narrow. A case whose `prompt` names material it does not carry still cannot be measured — both arms fail identically. Give such a case a `behaviour_prompt` restating the request with the material inlined; only this runner reads it, so `prompt` stays realistic for trigger evaluation. For manual transcript review, `--show-responses` prints both answers to stdout; use it only with eval inputs safe to display.

Four rules for reading trigger-eval results, all learned the expensive way:

- **Re-check on the model you actually run before calling a case a defect.** The default judge is the cheapest model, and it manufactures failures the production model does not have — three cases that sat at 0.33-0.5 for a whole review pass came back 5/5 on a larger judge. A candidate description was drafted, a skill was split in two, and both were rolled back before that check was run. The same instrument error recurred on 2026-07-29 in a five-case run: #24 scored 0.33 and #27 scored 0.00 at haiku, and both passed 9/9 at sonnet — two manufactured failures out of five, one of them on a case written that same day, which would have been "fixed" by rewriting a case that was never broken. #19 failed on both judges and is a genuine boundary against `frontend-verification`, unresolved at N=9 either side of that day's edit.
- **Before promoting a red case to a documented boundary, check which judge produced the red.** One eval — a one-page HTML dashboard of metrics for a team — was recorded here as routing to a runtime's built-in data-visualisation skill, kept red on purpose, and cited as a boundary this catalog had conceded. Re-measured on 2026-07-29 at sonnet, N=9, it passes 9/9 to `reader-facing-writing` — and does so identically on both sides of that day's description edit. The red was the cheap judge's, not the production model's: the first reading rule above, applied to a record this file had already built on. Two mechanical facts make the original reading unreproducible anyway — `run_trigger_evals.py` shows the judge only skills it can read from disk, and a runtime's built-ins are compiled into its CLI, so a built-in dataviz can appear only as a name the judge invents, scored `other:`. What survives is a directory fact, not an eval result: Codex's `.system/` ships imagegen, openai-docs, plugin-creator, review-agent, skill-creator, and skill-installer, and no chart or visual-design skill at all. Deferring to a neighbour only one runtime installs therefore belongs in the body, where it can depend on what is loaded, not in the description every runtime shares.
- **A description clause that only names an agent-internal moment cannot trigger, however real the rule behind it is.** Triggering is decided on the user's words, so a clause describing a situation the agent lands in mid-task has no user phrasing to match. `frontend-verification#15` — a browser submission interrupted halfway, asking whether to just redo it — is the recorded case: it judges 0/9 with the judge answering `none`, so no skill claims it at all. The rule it comes from (the record may already exist; re-query by id instead of resubmitting) is correct and stays in the body, where it fires once the surrounding browser task has already loaded the skill. The case is kept red as the measurement, not rewritten until it passes. Write clauses from how a user opens the request; audit the description for clauses that fail this test before spending characters on new ones. That audit ran on 2026-07-27 across all five descriptions: the interrupted-flow clause was the only one it found — every other "Also use when …" clause has a user-phrased eval case behind it — and it was deleted from `frontend-verification`'s description (887 → 816 characters), moving every surviving trigger earlier. The rule stays in the body and the case stays red; a clause measured at 0/9 has no triggering value to lose.
- **A single run decides nothing, and neither does a small total.** The same unchanged description scored 33/36 and 30/36 on identical cases, so differences inside that band are noise. Judge borderline cases at N≥9 and compare Wilson intervals per case, not summed pass counts — a candidate that wins one boundary case while losing another nets to zero, which is what most description edits do once a skill's cases already pass.

What the host does to a description before the model sees it, and what that forces on its shape — read against `codex-rs/core-skills/src/render.rs` on 2026-07-27, not from the docs page:

- **Over 1,024 characters, a description is cut to a 1,021-character prefix plus `...`.** Characters, not tokens; per skill; applied before any budget arithmetic. This is the same 1,024 the Agent Skills spec states, but the host enforces it by truncating rather than by rejecting the skill.
- **The rendered skill list has a second, shared budget: 2% of the model's context window, or 8,000 characters when the window is unknown.** Every entry costs its name and file path too, not just its description.
- **Over that budget, descriptions are cut to prefixes — never summarized, never trimmed clause by clause.** The host hands out description characters one at a time, round-robin across skills, so each keeps a similar number of *leading* characters and everything past that point is gone. Tighter still, and whole skills drop out of the list.
- **So clause order is mechanical, not stylistic: the tail dies first.** Lead with the request phrasings the skill must win; leave boundary clauses (`Not for …`) and rare triggers last. OpenAI's skills documentation gives the same instruction — front-load the key use case and trigger words — for exactly this reason.
- **`run_trigger_evals.py` cannot see any of this.** It judges through `claude -p`, where nothing truncates. A description can measure fine there and still arrive on another host with its last third missing.

Measured on the maintainer's machine the same day: 13 installed skills render to 3,189 tokens against a 5,440-token budget (2% of a 272k window) — comfortable — but 11,194 characters against the 8,000-character fallback, which the unknown-window path would truncate. This catalog is one of several installed side by side, so its five descriptions cannot be sized against their own sum alone; the consuming repo's resident-budget test bounds this catalog's share, and front-loading is what protects a description when a *neighbouring* catalog is what overruns the budget.

Already-tested dead ends — do not re-run these:

- **`change-discipline`'s description is at a local optimum.** Four candidates were measured against the shipped text: hard-gate-first while keeping the long facet enumeration (22/30 vs 21/30, overlapping intervals); two added sentences paid for by two deletions (#4 dependency direction fell 3/3 → 0/3); a pure 36-character addition (inside noise); and a pure 49-character addition that took #18 from 5/9 to 8/9 while dropping #24 from 7/9 to 2/9. Every candidate that wins a boundary case loses another. The one change that did land — hard gate first, facet enumeration trimmed, `splitting a large module` kept — is already in the shipped text.
- **Splitting `change-discipline` in two was actually built and rolled back.** A `boundary-and-style-review` sibling taking the boundary/contract and style facets scored 29/34 (85%), and a second pass at drawing the two descriptions apart scored 27/34 (79%), against 27/29 (93%) merged. The failures are the facet skill's cases being pulled back to the hard gate, and no wording fixes it: a user asking for either one says "change this existing code", so the two territories genuinely coincide in user phrasing.
- **When simulating a split or merge, the hit criterion must match the real eval.** The pre-split simulation counted "routed to either half" as a hit — measuring whether the request reached the catalog, not whether it reached the correct skill — and overestimated the gain as 53/55 vs 47/55, pointing the opposite way from the real result.
- **`reader-facing-writing`'s two candidates both net to zero.** Appending a form checklist took #13 to 3/3 but dropped #16 from 3/3 to 1/3; writing the same content mid-description tied outright. Those cases sit near a true rate of 0.5, where wording only moves wins between them.
- **A third `reader-facing-writing` candidate also netted zero.** On 2026-07-29 the closing clause went from `not to render the chart itself` to `charts included` (1021 → 1006 characters). At sonnet, N=9, case #4 measures 9/9 on both sides and case #19 moves 0.44 → 0.56 with the intervals overlapping — noise, not a gain. The edit was kept for two reasons that are not triggering: an unconditional refusal of charts in the description contradicts the conditional deference now in `references/visuals-and-decks.md`, and the shorter clause buys 15 characters of headroom against the 1,024-character truncation. Do not re-measure this clause expecting a trigger win.

Operationally: assert a candidate description is ≤1024 characters and re-read the file to confirm it was written before starting a run, chaining the write and the run with `&&`. Two runs have been wasted measuring an over-length text, or measuring a file that was never written.

Runtime adaptation rules:

- `SKILL.md` is the single source of truth for the workflow, and it is the only file every runtime loads. Keep it open-standard: name capabilities (a browser tool, a task tracker) rather than one runtime's tool names.
- Codex/OpenAI-specific config goes in `agents/openai.yaml`, with `default_prompt` explicitly referencing `$skill-name`.
- Do not add per-runtime notes beside it. This catalog shipped `agents/{claude,codex,antigravity}.md` until it was confirmed that nothing read them — no `SKILL.md` referenced them, no distribution code opened them, and a runtime loads no unreferenced file from a skill directory. A file no runtime reads cannot adapt anything; it only drifts against `SKILL.md`. If a runtime later gains a real convention, add it only with the loader named.

## How to Use

You don't need to adopt any fixed installer; this repository emphasizes the portability of the skill packages themselves.

Common usage:

1. Pick the skill directory you need.
2. Copy that directory into your agent skills path, or bring it into your own repo as a subdirectory / submodule.
3. Make sure the runtime can discover `SKILL.md`.
4. Let the agent invoke it via the skill's natural-language trigger conditions, reading `references/` or running `scripts/` on demand as needed.

The repository itself stays runtime-neutral and does not additionally maintain project-level wrappers for Claude Code, Codex, or Antigravity CLI.
If you want to use these skills within a specific runtime, the consuming side should place the skill in that runtime's required discovery path.

Skills split out of the rule system should carry only low-frequency, topic-specific workflows that need on-demand loading. Always-on rules retain only trigger conditions, constraint boundaries, and the minimal collaboration protocol; execution steps, checklists, failure boundaries, and verification details are maintained in the corresponding skill.

## Skills That Fit This Repository

- Engineering workflows the team will encounter repeatedly
- Tasks that easily go off track if explained only verbally
- Tasks that need clear failure boundaries, escalation conditions, and verification evidence
- Tasks whose repeated steps can be distilled into `references/` or `scripts/`

## Content That Does Not Fit This Repository

- One-off project notes
- Internal conventions that apply only to a single repo and cannot be abstracted for reuse
- Long documents with conceptual advice but no execution closed loop
- Mechanical rules that are better implemented as lint / script / CI checks

## Contribution Guidance

- One skill per directory, with names as clear and direct as possible.
- `SKILL.md` keeps only the core workflow; don't stuff README, CHANGELOG, or installation instructions into the skill package.
- Distill repeated and fragile steps into `scripts/` first, instead of restating them over and over in prose.
- Write trigger conditions for real user requests, not as abstract slogans.
- When targeting Claude Code, Codex, and Antigravity CLI at the same time, keep `SKILL.md` open-standard — name the capability, not one runtime's tool — instead of writing per-runtime files no runtime reads.
- If a skill is meant for repeated team use, it should at least be able to answer:
  - who will use it
  - how the user will trigger it
  - the minimum context to gather before execution
  - how to prove the task is truly complete
  - when to stop or escalate

If you use Codex's `skill-creator`-family toolchain, we recommend running a structure check and a team audit before submitting.

## Suggested Project Description

A short description suitable for the GitHub repository settings page:

`Open-source, team-grade skills for safe merges, rule-derived workflows, and reusable agent execution.`
