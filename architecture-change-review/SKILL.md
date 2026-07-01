---
name: architecture-change-review
description: Review architecture, shared interfaces, dependency boundaries, config schemas, workflow contracts, or module ownership changes before editing. Use when introducing new modules, changing public APIs, touching cross-layer dependencies, changing config defaults or migrations, or deciding whether a new abstraction is justified.
---

# Architecture Change Review

## Workflow

1. Identify the boundary being changed.
   - Name the current entry point, callers, owners, and generated or synced outputs.
   - State whether the change is local, shared, cross-module, or cross-repository.
   - **Establish WHY the current behavior/contract/default exists before changing it**: `git log -S "<symbol>"` / `git blame` the entry point. A behavior is often the deliberate result of an earlier `fix:[#…]`; reverting it re-opens that bug. A failing test or symptom does NOT by itself prove the current behavior is wrong — decide direction from history + the real contract, not from the symptom.
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
5. Verify before completion.
   - Run the smallest test that can catch the boundary mistake.
   - Re-read the final diff for circular dependencies, unclear ownership, or accidental public surface expansion.

## Stop Conditions

- The proposed abstraction has no concrete caller.
- The migration or rollback path is unknown.
- A dependency boundary would be crossed only to make the current patch easier.
- A change is routed through shared or public code when a leaf/endpoint placement would achieve the same result, with no stated reason.
- A split would only chase a size threshold, with no responsibility boundary behind it.
- The current behavior you are about to change is a deliberate earlier fix (per git history) whose intent you have not confirmed, or the change sits on an unresolved design/security/contract decision — escalate with the evidence instead of picking a side.
