---
name: change-discipline
description: Disciplined-change practices for editing existing code, config, schemas, data contracts, or architecture boundaries. Use for boundary work — changing shared interfaces, public APIs, dependency boundaries, config defaults or migrations, splitting large modules, or deciding whether a new abstraction is justified; and for style-and-contract work — code style, naming, input validation, serialized config, public contract fields, or comments. Both share one pre-change gate — establish why the current behavior exists before changing it, treat a symptom as evidence not spec, check callers and blast radius, verify the smallest thing, and escalate unresolved design/security/contract decisions.
---

# Change Discipline

Applies whenever you edit something that already exists. Start with the hard gate, then use the facet that matches the change — boundary/architecture, or style/naming/validation/comments. Many changes touch both. The gate is a lightweight always-on habit; the two facets below apply only when the change actually has a boundary or a style/contract dimension.

## Before you change anything that already exists (hard gate)

Applies to EVERY edit of existing code, a config/contract value, a default, a test expectation, or any behavior — not only bug fixes. The mistake this prevents: treating a symptom (a failing test, a "wrong-looking" value/regex/field name, a reported defect) as the spec and flipping the code to match it, thereby re-introducing a bug a previous commit deliberately fixed.

- **Establish WHY the current state is what it is, before changing it.** Run `git log -S "<symbol/value>"`, `git log -L`, or `git blame` on the exact line/symbol/default you intend to change. Current behavior is often the deliberate result of an earlier `fix:[#…]` / `feat:`; the commit message + bug id tell you the intent. Two real near-misses: a removed dangerous-char `;` (its removal had fixed a log-download bug) and a removed mode-guard (its removal had restored automatic failover) — re-adding either to satisfy a stale test would have re-opened the bug.
- **A symptom is not a spec — decide DIRECTION from history + the real contract, not from the symptom.** Current behavior is a deliberate later decision → the test/expectation is **stale**: update it and record which commit/bug voided the old one. The test/contract is right and the code is incomplete (e.g. committed together yet contradicting) → change the code. Never flip a value or loosen a check just to make a symptom disappear.
- **Grep every caller/consumer of a shared symbol, signature, contract field, or config key before changing it, and run the neighboring tests.** A change that satisfies one site can break a real caller (e.g. a guard added for one test that blocks an automatic background path). Widening/loosening can't break existing-valid inputs but can have a security blast radius — check that too.
- **Verify the smallest thing that can actually fail, then prove no new regression.** Run the narrowest test that exercises the change and read the REAL result (`BUILD SUCCESSFUL` / `N failed`), never a piped command's `| tail` exit code. Before declaring done, confirm zero new failures (diff the failing set against a clean baseline). One fix often unmasks deeper drift — a unit is not done until its whole class/module is green.
- **If history shows the change sits on an unresolved design / security / contract decision, stop and escalate with the evidence instead of silently picking a side.** Leaving it unchanged-and-flagged is a valid outcome; quietly satisfying a symptom you lack the authority to interpret is not.

## Boundary and architecture

1. Identify the boundary being changed.
   - Name the current entry point, callers, owners, and generated or synced outputs.
   - State whether the change is local, shared, cross-module, or cross-repository.
2. Prefer the smallest local change.
   - Do not introduce a new abstraction unless there are at least two real consumers or a clear boundary problem.
   - Keep existing framework, helpers, and dependency direction unless the current boundary is the bug.
   - When a file or function has grown large and mixes responsibilities, split it along existing responsibility seams (extract a module or function), not by an arbitrary line count; leave generated artifacts, data, vendored code, and large test files alone.
   - **Not impacting other business is the first-priority constraint.** In the design phase, evaluate whether the change can live at a leaf/endpoint instead of in shared or public code, and state the blast radius (which other callers of the shared symbol it touches). Route through shared/public code only when a leaf placement genuinely cannot achieve the same result — and say why. A real regression came from doing data-masking in shared code and breaking many unrelated features when the correct place was the endpoint.
   - Importing external best-practice guidance is itself an abstraction decision: first inventory what the current rules/skills already cover, judge each item by necessity × existing-coverage × where it belongs, and prefer folding it into an existing skill/rule over creating a new one. A new skill needs ≥2 real consumers or a clear gap — do not copy an external guide wholesale.
3. Check dependency direction.
   - UI or CLI may depend on application/service code.
   - Application code may depend on domain code.
   - Infrastructure details should stay behind adapters instead of leaking inward.
4. Define contract changes explicitly.
   - For config, schema, or workflow changes, state defaults, failure mode, rollback path, and whether migration is required.
   - For shared helpers or public surfaces, keep the interface narrow and name the concrete caller or test that justifies it.
5. Verify the boundary before completion.
   - Beyond the hard gate's smallest-test run, re-read the final diff for circular dependencies, unclear ownership, or accidental public-surface expansion.

## Style, naming, validation, comments

1. Match the local style first.
   - Use the repository's established formatter, lint, type-check, naming, and file layout.
   - New warnings introduced by your change count as regressions.
2. Use names with business meaning.
   - Avoid single-letter names and unclear abbreviations outside tiny local scopes.
   - Keep public fields and config keys consistent with existing contracts.
3. Validate inputs fail-close.
   - Reject malformed, unsupported, or ambiguous external input and config.
   - Do not silently coerce values unless an existing compatibility contract requires it.
   - In serialized config (YAML/TOML/JSON), keep values from changing the parse. An unquoted YAML scalar containing `: `, a leading `#`, or a `|`/`>` can silently reparse as a nested map, a comment, or a block scalar and load as the wrong thing — and a naive `split(":")` check won't catch it (a real case: an unquoted `description:` with `: ` in it made two skills silently fail to load). Quote the scalar, use ` — ` as an inline separator, and validate with a real parser, not string slicing.
4. Keep comments rare and useful.
   - Explain invariants, edge cases, or tradeoffs.
   - Do not narrate obvious line-by-line behavior.
5. Re-read the diff before completion.
   - Remove accidental churn, dead code, debug leftovers, misleading names, and stale comments.
   - Before deleting code, confirm why it exists (check version-control history) and that it is truly dead.
   - When told a resource is retired/no-longer-maintained, do a full-footprint sweep (`git grep` across code, tests, docs, Makefile, config, and wiring) and handle sibling retired resources together — do not clean up only the one that was named while leaving the rest half-removed.
   - Distinguish a tombstone guard (a test asserting a removed feature stays gone — safe to delete along with the feature) from a build-safety/security guard (content or invariant checks kept for a build or security reason). The commit that added the guard tells you which; do not delete the latter as "redundant".

## Stop Conditions

- The current behavior you are about to change is a deliberate earlier fix (per git history) whose intent you have not confirmed, or the change sits on an unresolved design/security/contract decision — escalate with the evidence instead of picking a side.
- The proposed abstraction has fewer than two real consumers and no clear boundary problem.
- The migration or rollback path is unknown, or a data contract change lacks a compatibility/migration story.
- A dependency boundary would be crossed, or a change routed through shared/public code, only to make the current patch easier when a leaf/endpoint placement would achieve the same result.
- A split would only chase a size threshold, with no responsibility boundary behind it.
- A style change would reformat unrelated files.
- A comment explains intent that should instead be expressed by clearer code.
