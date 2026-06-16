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
| [fix-ones-bug](./fix-ones-bug/SKILL.md) | Batch-processes ONES defects for "one owner x one iteration/version," covering investigation, fixing, regression, evidence, and status transition. Project-neutral (connects to any ONES project via a discoverable project profile); a root cause must be cross-confirmed by >=2 independent pieces of evidence before fixing, and stops to consult the user when changes are large or risky; ships with triggering evals. |
| [qa-self-verify](./qa-self-verify/SKILL.md) | Batch self-verifies fixed defects in a real QA/remote environment, captures UI evidence and writes it back to ONES, without writing code. Project-neutral: login method / environment entry / frontend route source are all discovered per project, not bound to a single codebase; ships with triggering evals. |
| [architecture-change-review](./architecture-change-review/SKILL.md) | Runs a boundary review before changing architecture, interfaces, dependency boundaries, config schemas, or cross-module contracts; ships with triggering evals. |
| [code-style-contracts](./code-style-contracts/SKILL.md) | Handles code style, config, data contract, naming, validation, and comment constraints, avoiding stuffing rule details into always-on context; ships with triggering evals. |
| [frontend-verification](./frontend-verification/SKILL.md) | Handles UI, browser automation, interactive HTML, responsive states, and frontend verification tool selection; ships with triggering evals. |
| [legacy-unit-test](./legacy-unit-test/SKILL.md) | Seeds meaningful characterization unit tests for low-coverage legacy code before refactoring, with risk maps, coverage maps, customer-defined coverage targets, and guardrails against behavior changes, low-value coverage, over-mocking, flaky tests, and unsafe snapshots; ships with triggering evals. |
| [artifact-hygiene](./artifact-hygiene/SKILL.md) | Decides the placement and cleanup boundaries for generated files, debug artifacts, Playwright evidence, downloads, and temporary scripts; ships with triggering evals. |
| [reader-facing-writing](./reader-facing-writing/SKILL.md) | Writes or revises reader-facing plans, reports, proposals, specs, checklists, Markdown, and HTML documents; ships with triggering evals. |

## Design Principles

- Evidence first: do not reach conclusions by guessing; the verification method and result must be stated.
- Closed loop first: form a complete path from trigger, context, execution, and verification through to reporting.
- Sharing first: reusable rules should be pushed down into a shared layer, not scattered across page patches or ad hoc notes.
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
│   │   ├── openai.yaml                 # Codex/OpenAI UI metadata
│   │   ├── codex.md                    # Codex tool mapping notes
│   │   ├── claude.md                   # Claude Code tool mapping notes
│   │   └── antigravity.md              # Antigravity CLI tool mapping notes
│   └── references/
├── fix-ones-bug/
│   ├── SKILL.md
│   ├── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
│   └── references/
├── qa-self-verify/
│   ├── SKILL.md
│   ├── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
│   ├── references/
│   └── scripts/
├── architecture-change-review/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
├── code-style-contracts/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
├── frontend-verification/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
├── legacy-unit-test/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
├── artifact-hygiene/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
└── reader-facing-writing/
    ├── SKILL.md
    └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
```

The top-level skill directories are the single source of truth, and the only content layer this repository maintains publicly.

Each canonical skill directory should be as self-contained as possible, typically including:

- `SKILL.md`: cross-runtime trigger conditions and the main workflow, kept open-standard and runtime-neutral
- `agents/openai.yaml`: Codex/OpenAI UI metadata and default invocation hints
- `agents/codex.md`: a thin adapter note for Codex tool mapping, progress tracking, and verification entry points
- `agents/claude.md`: a thin adapter note for Claude Code commands, tool mapping, and safety considerations
- `agents/antigravity.md`: a thin adapter note for Antigravity CLI invocation, progress tracking, and tool boundaries
- `references/`: reference material loaded on demand (when a single file exceeds 100 lines, put a table of contents at the top so a partial read still conveys the full picture)
- `scripts/`: fragile steps suitable for distilling into deterministic helpers
- `evals/evals.json`: triggering and behavioral evaluation cases, with positive cases covering the triggering scenarios in `description`, and negative cases guarding against false triggers or confirming routing to a sibling skill

All 9 current skills already ship with `evals/evals.json`, aligning with Anthropic's "evals first" skill authoring practice.

Runtime adaptation rules:

- `SKILL.md` is the single source of truth for the workflow; adapters may only map tools, invocation methods, and runtime safety restrictions.
- Codex/OpenAI-specific config goes in `agents/openai.yaml`, with `default_prompt` explicitly referencing `$skill-name`.
- Claude Code-specific invocation methods, tool names, and dynamic context-injection restrictions go in `agents/claude.md`, not in core.
- Codex-specific tool conventions (such as plan tracking, local browser selection, image viewing) go in `agents/codex.md`, not in core.
- Antigravity CLI-specific invocation methods, plan / status surfaces, and tool boundaries go in `agents/antigravity.md`, not in core.
- Adapters may not add, remove, or relax the verification gates, stop conditions, and status-transition requirements in `SKILL.md`.

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
- When adapting to Claude Code, Codex, and Antigravity CLI at the same time, keep `SKILL.md` open-standard and converge runtime differences into the `agents/` adapters.
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
