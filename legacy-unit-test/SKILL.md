---
name: legacy-unit-test
description: Adds meaningful characterization unit tests to low-coverage legacy code without changing production behavior. Use when a project needs test seeding before refactoring, customer-defined coverage progress, a risk map, a coverage map, or guardrails against low-value coverage padding, over-mocking, flaky unit tests, or unsafe snapshot approval.
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
- Do not approve or mass-update snapshots without human review of the changed behavior.
- Do not use test reruns, quarantine, skip, xfail, or broad retries as a substitute for fixing nondeterminism.

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
- code that changes often, will live for a long time, or is expensive to break
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

If code is hard to test because it directly reads time, randomness, environment, global state, files, databases, or network services, document the needed seam and stop for approval instead of changing production code inside the test-seeding task.

### 4. Write characterization tests

Lock observed behavior:

```text
fixed input -> call the real public logic -> assert the observed output or state change
```

Write tests through the public entry point of the unit under test whenever possible. Avoid testing private methods, helper internals, or implementation-only call sequences unless there is no stable public behavior to observe; if you must do so, document the limitation in `docs/testing/coverage-map.md`.

Cover the highest-value cases first:

- normal path
- boundary values
- null, empty, or invalid input
- important branches
- dependency failure
- state transition
- error behavior

Mock external dependencies only. Do not mock the method or business logic under test.

Prefer state or output assertions over interaction assertions. Verify calls on mocks only when the interaction itself is the contract, such as publishing an event, charging a payment provider, sending a notification, or invoking a retry/backoff policy.

Keep each test clear:

- Name the method or entry point, scenario, and observed behavior.
- Use Arrange, Act, Assert or the local equivalent.
- Prefer one Act per test.
- Use the smallest inputs that expose the behavior.
- Keep expected values explicit; avoid recomputing expected results with logic that mirrors production code.
- Avoid loops, conditionals, random data, and broad shared setup in tests unless they make the case clearer.
- Prefer descriptive duplication over hidden helper logic when it makes the test easier to audit.
- Use assertion helpers that produce useful failure messages.

Good unit tests must be fast, isolated, repeatable, and self-checking. If a test needs real infrastructure, real network, real external services, uncontrolled wall-clock time, uncontrolled randomness, or cross-test ordering, classify it as integration or smoke coverage instead of counting it as meaningful unit-test coverage.

If behavior looks wrong, record it in `docs/testing/suspicious-behavior.md` with:

- observed behavior
- why it is suspicious
- test file that locks it
- recommended product decision
- status: recorded only, not fixed

### 5. Use approval or snapshot tests carefully

Approval, golden-master, and snapshot tests are valid for legacy code only when their output is reviewable and stable.

Use them when the behavior is broad, hard to assert field-by-field, or valuable as a regression net. Avoid them when a small explicit assertion would be clearer.

When capturing output:

- Build a printer or normalizer that removes volatile data such as timestamps, random IDs, ordering noise, machine paths, locale-specific formatting, and environment-specific values.
- Keep approved output small enough for a human to review.
- Explain what business behavior the approved output represents.
- Treat snapshot updates as behavior-review events, not mechanical coverage maintenance.
- Do not store secrets, real customer data, tokens, internal hostnames, or environment-specific identifiers in approved outputs.

If a snapshot diff is large or unclear, replace it with focused assertions or split the output into smaller reviewable approvals.

### 6. Measure meaningful coverage

Use the customer-defined coverage target as an input value. Do not hardcode a percentage into the skill, tests, or docs.

Coverage is an indirect risk signal, not proof of quality. Use it to find untested high-risk lines and branches, then inspect whether the tests assert meaningful behavior.

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

Prefer branch or condition coverage when the toolchain supports it and the target has important branching. Consider mutation testing only as an optional later audit for critical modules because it can be much slower and may require team buy-in.

Update `docs/testing/coverage-map.md` after each batch with the target, measured coverage, tested modules, cases covered, remaining gaps, and next priorities.

When the customer requires a repository-wide target, still report:

- overall coverage
- meaningful coverage for core modules
- uncovered high-risk branches
- low-value coverage that should not be counted as progress

### 7. Verify the batch

Run the smallest relevant test first. Then run the broader unit test or coverage command when available and reasonable.

If a command cannot run, is unsafe, or does not exercise the change, state that explicitly and do not claim completion from that command.

Before reporting done, run a pitfall check:

- no production code changed without approval
- no test asserts only `not null`, object construction, or mock calls without behavior
- no test reproduces production logic to calculate the expected value
- no broad snapshot was added without a stable printer or human-reviewable output
- no real network, external service, database, uncontrolled time, uncontrolled randomness, or order dependency is required for unit tests
- no existing failing test was skipped, deleted, weakened, or quarantined
- no coverage target was hardcoded
- no suspicious behavior was fixed inside the test-seeding task

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
