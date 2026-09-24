# Boundary and architecture

Read this when the change crosses or defines a boundary: a shared symbol, a public
interface, a dependency direction, a new abstraction about to be introduced, a config
or schema contract, a file that exists as copies across repos, a module that has grown
to mix responsibilities, or an audit or exploration delegated to subagents that must
stay read-only.

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
   - A feature that snapshots data on its own, such as a pre-upgrade config backup, is opt-in and off by default rather than producing a copy on every run.
   - For a setup, provisioning, sync, or migration action meant to run more than once, state and ensure it is idempotent: re-running converges to the same state — applying only the missing delta and pruning what no longer belongs — instead of duplicating, clobbering, or failing on the second run. A non-idempotent re-run is a defect for anything automated or re-entrant.
   - For shared helpers or public surfaces, keep the interface narrow and name the concrete caller or test that justifies it.
5. Verify the boundary before completion.
   - Beyond the hard gate's smallest-test run, re-read the final diff for circular dependencies, unclear ownership, or accidental public-surface expansion.
   - Delegate audits and exploration to subagents as read-only finders and apply their findings yourself. An after-the-fact check proves nothing without a before value, so before dispatching record, per repository, `git rev-parse HEAD`, `git status --porcelain`, and `git ls-remote origin`; after they finish, run the same three and compare. A new commit, a changed file, or a moved remote ref is a violation to report before using any finding — parallel subagents have ignored read-only instructions and pushed as the user before.
