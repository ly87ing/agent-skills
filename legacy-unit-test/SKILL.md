---
name: legacy-unit-test
description: Adds meaningful characterization unit tests to low-coverage legacy code without changing production behavior. Use when a project needs test seeding before refactoring, customer-defined coverage progress, a risk map, a coverage map, or guardrails against low-value coverage padding.
---

# Legacy Unit Test

## Outcome

Build a safe unit-test seed for a legacy repository:

- current behavior is locked before refactoring starts
- high-risk business logic receives meaningful coverage first
- production behavior stays unchanged
- customer coverage targets remain configurable, not hardcoded
- gaps, suspicious behavior, and verification evidence are recorded

## Hard Boundaries

- Treat production code as read-only by default.
- Do not refactor production code while adding tests.
- Do not fix bugs unless the user explicitly asks for a separate bug-fix task.
- Do not change public APIs, database schema, build behavior, runtime config, or business behavior without approval.
- Do not write tests only to inflate coverage.
- Do not test trivial DTOs, data containers, getters, setters, simple mappers, or simple CRUD unless they contain real business logic.
- Do not delete tests, skip tests, loosen assertions, or make failures easier to pass.
- Stop before adding dependencies, changing CI, changing build scripts, or introducing production-code test seams.

## Required Outputs

Create or update these files when the repository does not already have equivalent artifacts:

- `docs/testing/current-baseline.md`
- `docs/testing/risk-map.md`
- `docs/testing/coverage-map.md`
- `docs/testing/suspicious-behavior.md` only when suspicious current behavior is found

## Workflow

### 1. Freeze the current baseline

Inspect the repository before writing tests:

1. Identify the language, build tool, test framework, test command, and coverage command.
2. Read README, Makefile, package/build files, CI config, and existing tests.
3. Run the smallest safe baseline command that could fail.
4. Record existing failures, missing commands, and unsafe commands without fixing production code.
5. Write the baseline into `docs/testing/current-baseline.md`.

### 2. Build the risk map

Choose targets by business risk, not by convenient coverage.

Prioritize:

- money, pricing, billing, payment, refund, discount, and settlement logic
- permission, authentication, authorization, role, and tenant-isolation logic
- state machines, lifecycle, workflow, approval, and task-transition logic
- branch-heavy validation or transformation logic
- recently changed, bug-prone, incident-related, or customer-critical modules
- service and domain logic with real business meaning

Defer:

- pure data containers
- simple CRUD
- simple mappers
- thin controllers with no business logic
- framework configuration and glue code

Write target reasoning, public entry points, dependencies, suggested cases, and priority into `docs/testing/risk-map.md`.

### 3. Add the smallest test support

Prefer the repository's existing test framework and local conventions.

Allowed without extra approval:

- fixtures under test directories
- mock factories for external dependencies
- small test helpers
- local coverage command wiring when the required tooling already exists

Requires approval first:

- new test dependencies
- CI changes
- build script changes
- production-code seams
- public API, schema, or runtime config changes

### 4. Write characterization tests

Lock observed behavior:

```text
fixed input -> call the real public logic -> assert the observed output or state change
```

Cover the highest-value cases first:

- normal path
- boundary values
- null, empty, or invalid input
- important branches
- dependency failure
- state transition
- error behavior

Mock external dependencies only. Do not mock the method or business logic under test.

If behavior looks wrong, record it in `docs/testing/suspicious-behavior.md` with:

- observed behavior
- why it is suspicious
- test file that locks it
- recommended product decision
- status: recorded only, not fixed

### 5. Measure meaningful coverage

Use the customer-defined coverage target as an input value. Do not hardcode a percentage into the skill, tests, or docs.

Count coverage as meaningful when it exercises:

- service or domain business rules
- state transitions
- validation rules
- branching logic
- error handling
- dependency failure behavior
- business-significant transformations

Do not count coverage as meaningful when it only:

- constructs objects
- asserts non-null values
- verifies mocks were called without checking behavior
- snapshots content with no reviewed business value
- touches trivial files to raise the aggregate metric

Update `docs/testing/coverage-map.md` after each batch with the target, measured coverage, tested modules, cases covered, remaining gaps, and next priorities.

### 6. Verify the batch

Run the smallest relevant test first. Then run the broader unit test or coverage command when available and reasonable.

If a command cannot run, is unsafe, or does not exercise the change, state that explicitly and do not claim completion from that command.

## Batch Discipline

Work in small batches. Prefer 1 to 3 high-risk modules per batch.

Do not attempt whole-repository coverage in one run unless the repository is small and the verification scope remains clear.

## Completion Evidence

Report:

- files changed
- tests added
- core logic covered
- commands run and exit results
- coverage result, if available
- production-code changes, expected to be none unless approved
- suspicious behavior recorded
- remaining gaps
- next highest-priority targets

Completion is not proven by a coverage number alone. Completion requires evidence that the tested logic is meaningful, behavior-preserving, and verifiable.
