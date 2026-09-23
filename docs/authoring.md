# Authoring Skills

How skill packages in this repository are designed, laid out, and contributed. The measurements behind these rules are in [evaluation.md](./evaluation.md).

## Design Principles

- Evidence first: do not reach conclusions by guessing; the verification method and result must be stated.
- Closed loop first: form a complete path from trigger, context, execution, and verification through to reporting.
- Sharing first: reusable rules should be pushed down into a shared layer, not scattered across page patches or ad hoc notes.
- Connector-first with a self-contained fallback: when a project ships a dedicated connector for an external system (issue tracker, CI, cloud), prefer it as the single source of truth; embedded raw HTTP or script templates are a documented fallback for runtimes without that connector, not a parallel source of truth. Because progressive loading does not cross skill boundaries, sibling skills cannot share one reference file, so the connector — not a shared file — is the point where that plumbing is deduplicated.
- Tool-neutral: enforce real observation of effects, but do not hard-bind to any one specific tool.
- Project-neutral: skills do not hardcode a single project's absolute paths, repo names, branches, internal UUIDs, or credential locations; project-specific information is injected via a discoverable project profile (resolved on demand or by asking the user), so the same skill can be reused across projects.
- Clear safety boundaries: spell out when it is okay to act automatically and when you must stop and escalate.
- Progressive loading: keep `SKILL.md` concise, push details down into `references/`, and push fragile steps into `scripts/` where possible. What the measurements found about where a rule has to live to fire is in [evaluation.md](./evaluation.md#progressive-loading-measured).

## Skill Package Layout

Each canonical skill directory should be as self-contained as possible, typically including:

- `SKILL.md`: cross-runtime trigger conditions and the main workflow, kept open-standard and runtime-neutral
- `agents/openai.yaml`: Codex/OpenAI UI metadata and default invocation hints — the only file in `agents/`, because it is the only one a runtime actually reads
- `references/`: reference material loaded on demand (when a single file exceeds 100 lines, put a table of contents at the top so a partial read still conveys the full picture)
- `scripts/`: fragile steps suitable for distilling into deterministic helpers
- `evals/evals.json`: triggering and behavioral evaluation cases, with positive cases covering the triggering scenarios in `description`, and negative cases guarding against false triggers or confirming routing to a sibling skill. Eval prompts may be written in the primary user's language (including Chinese) to test real trigger phrasing — as may the optional `behaviour_prompt` that restates one of them with its material inlined for the behaviour runner; every other field stays English.
- `tests/`: per-skill unit tests guarding fragile script logic, run automatically by the top-level suite

All seven current skills already ship with `evals/evals.json`, aligning with Anthropic's "evals first" skill authoring practice.

## Runtime Adaptation Rules

- `SKILL.md` is the single source of truth for the workflow, and it is the only file every runtime loads. Keep it open-standard: name capabilities (a browser tool, a task tracker) rather than one runtime's tool names.
- Codex/OpenAI-specific config goes in `agents/openai.yaml`, with `default_prompt` explicitly referencing `$skill-name`.
- Do not add per-runtime notes beside it. This catalog shipped `agents/{claude,codex,antigravity}.md` until it was confirmed that nothing read them — no `SKILL.md` referenced them, no distribution code opened them, and a runtime loads no unreferenced file from a skill directory. A file no runtime reads cannot adapt anything; it only drifts against `SKILL.md`. If a runtime later gains a real convention, add it only with the loader named.

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
