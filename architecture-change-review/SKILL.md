---
name: architecture-change-review
description: Review architecture, shared interfaces, dependency boundaries, config schemas, workflow contracts, or module ownership changes before editing. Use when introducing new modules, changing public APIs, touching cross-layer dependencies, changing config defaults or migrations, or deciding whether a new abstraction is justified.
---

# Architecture Change Review

## Workflow

1. Identify the boundary being changed.
   - Name the current entry point, callers, owners, and generated or synced outputs.
   - State whether the change is local, shared, cross-module, or cross-repository.
2. Prefer the smallest local change.
   - Do not introduce a new abstraction unless there are at least two real consumers or a clear boundary problem.
   - Keep existing framework, helpers, and dependency direction unless the current boundary is the bug.
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
