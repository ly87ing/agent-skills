---
name: change-discipline
description: Applies to every edit of something that already exists, however small — an in-place bug fix, a refactor, a config or default value, a schema, a test expectation, or a contract. Establish why the current behavior exists before changing it, treat a symptom or a reported root cause as a lead needing independent confirmation rather than a spec, check callers and blast radius, and verify the smallest thing that can actually fail. Use it too when an empty search or a clean git status may be an ignore-rule illusion, when an audit is delegated to subagents that must stay read-only, when a finding would reverse a call the user already made, for unexplained working-tree changes of unknown authorship, for a file synced across repos, and for the boundary or style dimension of an edit — dependency direction, public interfaces, config migrations, splitting a large module that mixes responsibilities, idempotent re-runs, new abstractions, naming, input validation, comments.
---

# Change Discipline

Applies whenever you edit something that already exists. Start with the hard gate, then use the facet that matches the change — boundary/architecture, or style/naming/validation/comments. Many changes touch both. The gate is a lightweight always-on habit; the two facets below apply only when the change actually has a boundary or a style/contract dimension.

## Before you change anything that already exists (hard gate)

Applies to EVERY edit of existing code, a config/contract value, a default, a test expectation, or any behavior — not only bug fixes. The mistake this prevents: treating a symptom (a failing test, a "wrong-looking" value/regex/field name, a reported defect) as the spec and flipping the code to match it, thereby re-introducing a bug a previous commit deliberately fixed.

- **Establish WHY the current state is what it is, before changing it.** Run `git log -S "<symbol/value>"`, `git log -L`, or `git blame` on the exact line/symbol/default you intend to change. Current behavior is often the deliberate result of an earlier `fix:[#…]` / `feat:`; the commit message + bug id tell you the intent. Two real near-misses: a removed dangerous-char `;` (its removal had fixed a log-download bug) and a removed mode-guard (its removal had restored automatic failover) — re-adding either to satisfy a stale test would have re-opened the bug.
- **A symptom is not a spec — decide DIRECTION from history + the real contract, not from the symptom.** Current behavior is a deliberate later decision → the test/expectation is **stale**: update it and record which commit/bug voided the old one. The test/contract is right and the code is incomplete (e.g. committed together yet contradicting) → change the code. Never flip a value or loosen a check just to make a symptom disappear.
- **Grep every caller/consumer of a shared symbol, signature, contract field, or config key before changing it, and run the neighboring tests.** A change that satisfies one site can break a real caller (e.g. a guard added for one test that blocks an automatic background path). Widening/loosening can't break existing-valid inputs but can have a security blast radius — check that too.
- **An empty search and a clean `git status` can both be ignore-rule illusions.** Before concluding "nothing matches" from a search run at a repo or hub root, check whether ignore rules silently excluded the directories you meant to search (nested sub-repos, dist dirs) and re-run with ignore rules off or with explicit paths. Symmetrically, a new file on an ignored path leaves `git status` clean without being tracked — `git add -f` (or fix the rule) and confirm it actually entered the commit. Real cases: a hub-root search nearly concluded a whole codebase did not exist; an ignored `test*` pattern silently kept new tests out of every push.
- **Verify the smallest thing that can actually fail, and read the real result.** Run the narrowest test that exercises the change and read the REAL result (`BUILD SUCCESSFUL` / `N failed`), never a piped command's `| tail` exit code.
- **When the change has no test to run, verify its effect against the primary source, not a proxy signal.** For a config value, a credential, a service, or a tool wiring, a `200`, an `exit 0`, a "loaded" log line, or a tool's own summary can be a false positive (a SPA answers 200 on any path; a running process keeps its old env until restarted; `git log -S` counts occurrences, so an in-place value swap never shows; a self-test under your own privileged account never reproduces a failure that was identity- or permission-scoped, so rerun it under the affected role, account, or condition). Hit the actual endpoint and read the body, or read the real stored value — not a status code or a count.
- **Prove no new regression before declaring done.** Confirm zero new failures by diffing the failing set against a clean baseline. One fix often unmasks deeper drift — a unit is not done until its whole class/module is green.
- **Confirm the diagnosis from independent angles before changing code — a wrong root cause yields a confident wrong fix.** Reason from the system's own observed behavior, not from the first hypothesis offered: a report that "it's X" — from the user, a teammate, or another agent — is a lead, not a verdict, so think it through from a blank slate. When two sources disagree about the cause, reconcile them with evidence rather than adopting the convenient one; the more consequential or non-obvious the cause, the more independent confirmation it needs (ideally two lines of evidence converging) before you act on it. If the fix that follows is large, cross-cutting, or otherwise high-risk, surface the diagnosis and the options and let the user choose the direction instead of proceeding silently.
- **If history shows the change sits on an unresolved design / security / contract decision, stop and escalate with the evidence instead of silently picking a side.** Leaving it unchanged-and-flagged is a valid outcome; quietly satisfying a symptom you lack the authority to interpret is not.
- **Escalation is for genuine uncertainty, not for a call the user has already made.** When the user has explicitly decided the direction or authorized the action, carry it out — do not re-confirm, re-litigate, or stall because a subagent or another agent disagrees. The stop-and-escalate above is reserved for an unconfirmed root cause, an unresolved design/security/contract decision, or a large, cross-cutting, or high-risk change — not for work the user has already settled.
- **A call the user already made also stays made when a review wants to reverse it.** A verified finding — from a review pass, a subagent, or your own later re-read — about something the user deliberately removed, rejected, or chose is a recommendation to raise, not a defect to apply: check history for the deliberate decision (`git log -S`, `git log --diff-filter=D`), surface it, and let the user rule. Naming it in your summary while applying it in the same pass is not consent. A real case: a review flagged a line the user had explicitly deleted as "missing", the agent restored it and added an in-tree comment telling future editors not to remove it again — reversing the user's call and then defending the reversal in the file.
- **Working-tree changes you did not make belong to a human until proven otherwise.** When files you never touched show up `deleted`/`modified`, assume the user edited them by hand and ask before acting on them; never `git restore .` / `git checkout .` / `git clean` over unexplained changes, and never attribute them to a sync service, an editor, or an environment glitch without first gathering evidence for that attribution. If you must clear the tree, `git stash` to preserve the state first. A real case: an agent blamed a batch of unexplained deletions on cloud-sync drift — on a machine with no such sync configured — and bulk-restored, silently undoing the user's own manual cleanup.

## Boundary and architecture

1. Identify the boundary being changed.
   - Name the current entry point, callers, owners, and generated or synced outputs.
   - State whether the change is local, shared, cross-module, or cross-repository.
2. Prefer the smallest local change.
   - Do not introduce a new abstraction unless there are at least two real consumers or a clear boundary problem.
   - Keep existing framework, helpers, and dependency direction unless the current boundary is the bug.
   - Before hand-rolling test scaffolding, a fixture, or a UI helper, search for what the repo already ships and reuse it — reinventing a component the project already provides is a defect, not a neutral choice. When the existing entry point was hard to discover, record it (a make target, a README line, a fixture path) so the next person or agent finds it without re-deriving it.
   - When the same file exists as copies across repos or packages (vendored, sync-distributed, generated), establish the single upstream before editing: land the fix upstream and let the sync fan it out, never patch only the downstream copy — the next sync silently reverts it. `diff` the copies first to learn which way drift actually flows.
   - When a file or function has grown large and mixes responsibilities, split it along existing responsibility seams (extract a module or function), not by an arbitrary line count; leave generated artifacts, data, vendored code, and large test files alone.
   - **Not impacting other business is the first-priority constraint.** In the design phase, evaluate whether the change can live at a leaf/endpoint instead of in shared or public code, and state the blast radius (which other callers of the shared symbol it touches). Route through shared/public code only when a leaf placement genuinely cannot achieve the same result — and say why. A real regression came from doing data-masking in shared code and breaking many unrelated features when the correct place was the endpoint.
   - **Resource impact is a first-class constraint too, not just business blast radius.** Anything that runs on shared or production infrastructure must bound its CPU, memory, disk, and IO footprint: sense real pressure and self-throttle (start conservative, ramp up, back off or pause new work when load/IO climbs), leave headroom instead of running at the machine's ceiling, and never let a batch or build job starve the platform it runs on. Maximizing a job's own throughput at the cluster's expense is a regression even when the job "succeeds".
   - Importing external best-practice guidance is itself an abstraction decision: first inventory what the current rules/skills already cover, judge each item by necessity × existing-coverage × where it belongs, and prefer folding it into an existing skill/rule over creating a new one. A new skill needs ≥2 real consumers or a clear gap — do not copy an external guide wholesale.
3. Check dependency direction.
   - UI or CLI may depend on application/service code.
   - Application code may depend on domain code.
   - Infrastructure details should stay behind adapters instead of leaking inward.
4. Define contract changes explicitly.
   - For config, schema, or workflow changes, state defaults, failure mode, rollback path, and whether migration is required.
   - For a setup, provisioning, sync, or migration action meant to run more than once, state and ensure it is idempotent: re-running converges to the same state — applying only the missing delta and pruning what no longer belongs — instead of duplicating, clobbering, or failing on the second run. A non-idempotent re-run is a defect for anything automated or re-entrant.
   - For shared helpers or public surfaces, keep the interface narrow and name the concrete caller or test that justifies it.
5. Verify the boundary before completion.
   - Beyond the hard gate's smallest-test run, re-read the final diff for circular dependencies, unclear ownership, or accidental public-surface expansion.
   - Delegate audits and exploration to subagents as read-only finders and apply their findings yourself; after they finish, run `git status` and `git ls-remote` to confirm no subagent committed or pushed under your identity — parallel subagents have ignored read-only instructions and pushed as the user before.

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
