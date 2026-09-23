# Delegation brief

Read this when the scheme is agreed and someone else, a person or an implementing agent, will build it. The coordinator keeps design, scope decisions, review, and acceptance; the implementer gets a brief that makes "done" unambiguous.

## What the brief contains

| Field | Content |
| --- | --- |
| Scope | The files, modules, and interfaces the implementer may change, and the ones they may not |
| Inputs and outputs | The contract each changed interface must keep or gain, with an example of each |
| Constraints | A link to the constraints table; the deployment model in one line |
| Acceptance criterion | Stated as "the end user can ..." — it builds, it is packaged or downloadable where the user expects it, the usage note exists |
| Verification to run | The narrowest tests that exercise the change, the real-input check, and the evidence to return (a result file, a diff, a screenshot of the decisive state) |
| Out of scope | What the implementer must not start, even if it looks adjacent |
| Stop conditions | The findings on which the implementer stops and reports instead of deciding |

## Rules

- "Code exists on a branch" is a lower rung than the acceptance criterion. Case: a delegated implementation stopped at "server capability done"; the user then had to ask separately for the CLI, the binaries, the download page, and the build script that produced them.
- The coordinator re-runs the decisive check and reads the diff; the implementer's report, its screenshot file, and its exit code are claims. The ladder that decides which rung the evidence reaches is in `verification`.
- One shared interface has one owner; when two implementers touch it, the brief names which one.
- A brief that cannot state the acceptance criterion as something the user can do is a scheme that is not finished; go back to the workflow before delegating.
