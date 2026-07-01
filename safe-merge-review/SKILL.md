---
name: safe-merge-review
description: Use when the user wants to merge a branch, a remote ref, or the corresponding branches across a set of related repos into the current working branch, or wants to review whether "this merge is correct", "anything was missed", "the conflict resolution is reliable", or "it is safe to push after the merge". Applies when the user provides a branch name, remote ref, repo path, conflicted files, a merge commit, a merge request link, or a multi-repo set of branches. Proves that "the merge is correct" rather than merely running git merge, through diff modeling, hotspot-overlap review, semantic re-review, completeness proof, minimal relevant verification, and a push decision.
---

# Safe Merge Review

## Outcome

Treat "merge succeeded" and "merge is correct" as two different things, and produce verifiable evidence:

- Which repos and which refs the current merge covers
- Whether the source changes really need to enter the current branch
- Which hotspot files and shared boundaries require deep reading
- Whether the conflict resolution preserved the necessary semantics from both sides
- Whether the source ref has been fully included in `HEAD`
- Whether the minimal relevant verification passes
- Whether the current result is safe to push, and what residual risks remain

## Roles and Jobs

- Engineering:
  - Safely merge the source branch into the current branch
  - Review whether the merge result has logical mismatches, missed merges, or wrong trade-offs
- Release / QA:
  - Decide whether a given merge is ready to continue verification, hand off to testing, or push
  - Perform per-repo evidence checks for coordinated multi-repo merges

## Trigger Matrix

| Trigger | Role | Required context | Path |
| --- | --- | --- | --- |
| "Merge `feature/foo` into the current branch" | Engineering | repo path + source ref | Path 1 + Path 2 |
| "Check whether this merge missed anything" | Engineering / QA | repo path + source ref or merge commit | Path 1 + Path 3 |
| "How should this conflict be resolved, and can I push after resolving it" | Engineering | repo path + conflicted files + source ref | Path 1 + Path 2 |
| "The corresponding branches in these repos all need merging; help me confirm whether it is correct" | Release / Engineering | repo list + source refs | Path 1 + Path 2 |
| "This branch looks already merged; help me prove whether it is really included" | Engineering / QA | repo path + source ref or merge commit | Path 3 |

## Context Sources

Collect the minimal context before starting:

- Repo scope:
  - Whether the current directory is a git repo
  - Single-repo or multi-repo
  - Current branch, target branch, source ref, remote
- Worktree state:
  - `git status --short --branch`
  - Whether there are uncommitted changes, staged changes, or a user's manual conflict-resolution work in progress
- Merge evidence:
  - Source ref or merge commit
  - Affected files, hotspot overlap, key incoming commits
  - Whether the repo uses a fast-forward, merge commit, squash, or other history strategy
- Verification context:
  - Minimal relevant verification commands
  - Whether each repo must be verified separately
- Risk boundaries:
  - Whether there is a dirty worktree, multi-repo coordination, submodules, binary files, large numbers of renames, or rebase/squash history
  - Whether a networked `fetch` is required

Environment prerequisites:

- A working git CLI and read/write access to the repo are required
- Judging a remote source ref usually requires a networked `fetch`

## Reference Loading Guide

Load references on demand instead of cramming every detail into the main flow:

- When you need command templates, the strategy matrix, patch-equivalent, or completeness-verification methods, read [references/merge-workflow.md](references/merge-workflow.md)
- When you need to judge hotspot risk, conflict semantics, or post-merge logical-mismatch patterns, read [references/merge-review-checklist.md](references/merge-review-checklist.md)
- When you need to generate a stable reporting skeleton, run [scripts/build_merge_evidence.py](scripts/build_merge_evidence.py)

## Workflow Paths

### Path 1: Model the diff and decide the merge plan

1. Stabilize the worktree.
   - First check `git status --short --branch`
   - Confirm the actual branch and worktree with `git rev-parse --abbrev-ref HEAD` + `git worktree list`; do not rely on a shell prompt or statusline (it can be stale or wrong). When the user named a target branch or worktree, assert HEAD matches it before editing or pushing — if it does not, stop and correct, rather than acting on the wrong line.
   - A dirty worktree is not merged directly by default; first state the risk, then decide whether to continue
2. Lock down the source and target refs.
   - Clarify the current branch, source ref, target ref, and remote
   - When the source ref is unclear, do not guess "the latest line"
3. Fetch the latest state and model the diff.
   - Prefer following [references/merge-workflow.md](references/merge-workflow.md) to run `fetch`, merge base, left/right counts, incoming commits, and file-set comparison
   - When the history shows signs of rebase / squash / rewrite, additionally run the patch-equivalent check
4. Identify the hotspot overlap and do a semantic pre-review.
   - Prioritize reviewing shared logic, public interfaces, config, schema, migrations, build scripts, tests, and generated artifacts that both sides changed
   - For high-risk files, review item by item per [references/merge-review-checklist.md](references/merge-review-checklist.md)
5. Choose a merge strategy.
   - When the source is already included, report `already contained` directly
   - For a non-trivial merge, default to a reviewable path: inspect the staged result first, then land the final commit

### Path 2: Execute the merge and prove the result is correct

1. Execute the chosen merge strategy.
   - Even fast-forward candidates first complete diff modeling and semantic pre-review
   - For a non-trivial merge, review the staged result first by default; do not treat "no text conflicts" as "no logical conflicts"
2. Resolve conflicts using three-way evidence.
   - For each conflicted file, look at base / ours / theirs
   - Record the final resolution and why no necessary semantics from the other side were lost
3. Prove "complete merge".
   - Prove the source ref is included in `HEAD`
   - Prove `HEAD..<source-ref>` is empty
   - For a squash merge, `is-ancestor` does not apply; choose an alternative proof method per [references/merge-workflow.md](references/merge-workflow.md) section 7.5 and annotate `proof-method`
   - List the files and diffs that actually landed
4. Do another post-merge semantic re-review.
   - Check whether the final code is just one side's logic winning by mistake
   - Focus on shared boundaries, initialization chains, configuration closure, default resources, and upstream/downstream repo coordination
5. Run the minimal relevant verification.
   - Run only the verification commands that could actually fail because of this merge
   - In multi-repo scenarios, record per repo; do not collapse into a single "all passed"
6. Decide whether to allow a push.
   - Push only when the user explicitly requests it or the process explicitly requires it
   - If any gate is skipped, you must explicitly state the reason and the residual risk

### Path 3: Audit a completed merge

1. Lock down the audit target.
   - Clarify whether you are auditing a specific merge commit, a specific source ref, or the current worktree result
2. Reconstruct the expected diff.
   - Recompute the merge base, incoming commits, file sets, and hotspot overlap
   - Do not equate "there is no diff now" with "it was merged correctly back then"
   - On parallel/independent baseline lines, the same logical change often lands via a **different commit and issue id** on each line; `is-ancestor <sha>`, a commit-id search, and an issue-number search can all report "missing" while the content is actually present. Judge "does this branch contain the fix" by the **file content / patch**, not the commit graph or issue id (see [references/merge-workflow.md](references/merge-workflow.md) section 3.4).
3. Check completeness and semantics.
   - Cross-check the source ref, the landed files, and the final code
   - Focus on the post-merge error patterns in [references/merge-review-checklist.md](references/merge-review-checklist.md)
4. Run the minimal relevant verification and produce a conclusion.
   - The conclusion can only be `Green / Yellow / Red`
   - It must come with an evidence matrix and residual risks

## Reusable Resources

### scripts/

- [scripts/build_merge_evidence.py](scripts/build_merge_evidence.py)
  Generates a stable merge-evidence Markdown skeleton for unified reporting of multi-repo or high-risk merges. Best run after the ref is locked down and the risk items are identified, to avoid evidence drift caused by hand-assembling fields each time.

### references/

- [references/merge-workflow.md](references/merge-workflow.md)
  Read for command templates, the strategy matrix, conflict-handling methods, and completeness-verification methods.
- [references/merge-review-checklist.md](references/merge-review-checklist.md)
  Read for hotspot risk, semantic issues, post-merge logical-error patterns, and the evidence-matrix template.

## Verification Matrix

| Path | Check | Evidence |
| --- | --- | --- |
| Path 1 | Source and target refs are locked down, and the diff set and hotspot files are modeled | merge base, left/right counts, incoming commits, hotspot file list |
| Path 2 | The merge result is fully included and the minimal relevant verification is complete | completeness proof, final landed files, verification commands and results, push decision |
| Path 3 | The correctness of a completed merge is re-audited | source ref / merge commit, semantic re-review conclusion, verification results, Green/Yellow/Red verdict |

## Failure and Escalation

Stop or escalate, instead of continuing to guess, when:

- The source ref, target ref, or remote is unclear
- A dirty worktree would contaminate the merge evidence, but the user has not yet confirmed a handling strategy
- You cannot `fetch` the latest source state but still need to judge a remote branch
- A destructive action is required (such as `reset`, `checkout --`, or force-overwriting the conflict result), but the user has not yet approved it
- In a multi-repo coordination, some repo lacks context, lacks a source ref, or lacks a verification command
- You cannot provide a minimal relevant verification, so you can only report "not verified" and cannot claim completion

## Reporting

After completing, report at least the following:

### Safe merge review summary
- repo:
- current branch:
- source ref:
- merge base:
- left/right counts:
- incoming key commits:
- hotspot overlap files:
- merge strategy:
- conflicted files and reasoning:
- completeness proof:
- proof method: (is-ancestor | patch-equivalent | tree-diff | cherry-pick-noop)
- semantic review conclusion:
- verification command(s):
- push status:
- residual risks:

For a multi-repo scenario, report per repo; do not substitute a single "all merged fine".
