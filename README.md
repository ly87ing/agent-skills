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

`frontend-verification` was merged into `verification` on 2026-09-21, because verification evidence was split across two skills and the non-UI rungs — tests, pushed, deployed, accepted — had no owner.

| Skill | Description |
| --- | --- |
| [safe-merge-review](./skills/safe-merge-review/SKILL.md) | Treats "merge succeeded" and "merge is correct" as separate concerns, emphasizing diff modeling, hotspot-overlap review, completeness verification, and the push decision; ships with triggering evals. |
| [change-discipline](./skills/change-discipline/SKILL.md) | Disciplined changes to existing code: one pre-change hard gate (establish why current behavior exists, symptom-is-not-spec, blast radius, smallest verification) plus two facets — boundary/architecture review and code style/contract/naming/validation/comment constraints; ships with triggering evals. |
| [solution-shaping](./skills/solution-shaping/SKILL.md) | Shapes a scheme before anything is built: constraints table, live-dead inventory, target state with its deployment model, blast-radius checklist, evidence-graded claims, and an implementer brief with acceptance criteria; ships with triggering and behavioural evals. |
| [verification](./skills/verification/SKILL.md) | Proves a change works at the rung it claims — target lock, delivery ladder (tests, pushed, deployed, verified, accepted), real-input old-new comparison, consumer path, delegated-work acceptance — with browser and rendered-surface evidence as its UI facet; ships with triggering and behavioural evals. |
| [artifact-hygiene](./skills/artifact-hygiene/SKILL.md) | Decides the placement and cleanup boundaries for generated files, debug artifacts, Playwright evidence, downloads, and temporary scripts; ships with triggering evals. |
| [reader-facing-writing](./skills/reader-facing-writing/SKILL.md) | Writes or revises reader-facing plans, reports, proposals, specs, checklists, Markdown, and HTML documents around per-artifact skeletons with page budgets, a form-by-content-shape table, per-medium figure rules, and before/after examples; ships with triggering and behavioural evals. |
| [technical-diagramming](./skills/technical-diagramming/SKILL.md) | Builds and verifies evidence-grounded architecture, deployment, workflow, sequence, data-flow, lifecycle, and topology-comparison diagrams; ships with triggering and behavioral evals plus deterministic SVG checks. |

All seven skills are self-contained and have no cross-skill prerequisites.

Self-contained does not mean that adjacent skills should duplicate one another. When
several of these skills are available for one task, compose them by phase and keep each
decision with one owner:

| Decision | Owner |
| --- | --- |
| Decide whether the reader needs a diagram, the reader question it must answer, its takeaway, and the surrounding material | `reader-facing-writing` |
| Model the technical nodes, edges, boundaries, and states; choose the layout; author and semantically validate the diagram artifact | `technical-diagramming` |
| Decide what to build or change and prove the scheme is complete before anything is edited | `solution-shaping` |
| Prove the built artifact in a browser: interactions, focus, zoom, contrast, overflow, responsive states, and console/runtime failures | `verification` |
| Decide file placement, redaction, cleanup, runtime-dependency packaging, and clean handoff | `artifact-hygiene` |

When the named owner is unavailable, the skill already in use may apply only its
documented minimum fallback and must report the resulting verification limit. A
fallback is not a second source of truth when the owner is present.

## Repository Structure

```text
agent-skills/
├── skills/
│   └── <skill>/                        # one directory per skill, see the catalog above
│       ├── SKILL.md                    # runtime-neutral source
│       ├── agents/openai.yaml          # Codex/OpenAI UI metadata
│       ├── evals/evals.json            # triggering and behavioural cases
│       ├── references/
│       ├── scripts/
│       └── tests/
├── rules/
│   ├── core.md                         # always-on rules for CLAUDE.md / AGENTS.md
│   ├── README.md                       # what may go in core.md, budget, measuring
│   └── evals/core.json
├── aliases/
│   ├── aliases.json                    # recommended terminal shortcuts
│   └── README.md                       # file shape and the rules Agent Manager enforces
├── docs/
│   ├── authoring.md                    # design principles, package layout, contributing
│   └── evaluation.md                   # model-backed runners, reading results, measurements
├── tools/evals/                        # model-backed eval runners and the built-in catalog fixture
└── tests/                              # offline gate: contracts, unit suites, runner harness tests
```

The directories under `skills/` are the single source of truth for the skills. `rules/` holds the always-on rule layer that the skills are designed against: `core.md` carries only universal invariants and no skill names, and [`rules/README.md`](./rules/README.md) records what may go in it. Agent Manager reads `rules/*.md` from this repository as rule templates, and `aliases/*.json` as recommended terminal shortcuts (see [`aliases/README.md`](./aliases/README.md)).

How a skill package is laid out, designed, and contributed is in [docs/authoring.md](./docs/authoring.md); how skills and rules are measured, and what the measurements found, is in [docs/evaluation.md](./docs/evaluation.md).

## Verification

- `python3 -m unittest discover -s tests` — structure/contract gate plus every per-skill unit suite, the rule budget and anchor checks, and the alias shape checks
- `npx skills-ref validate ./skills/<skill>` — the Agent Skills reference validator, run per skill; optional because it needs the network, while the suite above stays offline and stdlib-only

The model-backed runners in `tools/evals/` are described in [docs/evaluation.md](./docs/evaluation.md#runners).

## How to Use

You don't need to adopt any fixed installer; this repository emphasizes the portability of the skill packages themselves.

Common usage:

1. Pick the skill directory you need under `skills/`.
2. Copy that directory into your agent skills path, or bring it into your own repo as a subdirectory / submodule.
3. Make sure the runtime can discover `SKILL.md`.
4. Let the agent invoke it via the skill's natural-language trigger conditions, reading `references/` or running `scripts/` on demand as needed.

The repository itself stays runtime-neutral and does not additionally maintain project-level wrappers for Claude Code, Codex, or Antigravity CLI.
If you want to use these skills within a specific runtime, the consuming side should place the skill in that runtime's required discovery path.

Skills split out of the rule system should carry only low-frequency, topic-specific workflows that need on-demand loading. Always-on rules retain only trigger conditions, constraint boundaries, and the minimal collaboration protocol; execution steps, checklists, failure boundaries, and verification details are maintained in the corresponding skill.

## Suggested Project Description

A short description suitable for the GitHub repository settings page:

`Open-source, team-grade skills for safe merges, rule-derived workflows, and reusable agent execution.`