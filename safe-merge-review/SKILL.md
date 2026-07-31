---
name: safe-merge-review
description: Use when the user wants to merge a branch, a remote ref, or the corresponding branches across a set of related repos into the current working branch, or wants to review whether "is this branch ready to merge", "this merge is correct", "anything was missed", "the conflict resolution is reliable", or "it is safe to push after the merge". Applies when the user provides a branch name, remote ref, repo path, conflicted files, a merge commit, a merge request link, or a multi-repo set of branches; also when confirming a fix is really present on a parallel release line that commit-id or is-ancestor searches report as missing, and when a merge decision turns on another repo's dependency not yet on the tracked ref. Proves that "the merge is correct" rather than merely running git merge, through diff modeling, hotspot-overlap review, semantic re-review, completeness proof, minimal relevant verification, and a push decision. Not for branch code-quality review while no merge, audit, or conflict is in play.
---

# Safe Merge Review

## Outcome

Treat "merge succeeded" and "merge is correct" as two different things, and produce verifiable evidence for every field of the Reporting skeleton at the end of this file — that field list is the definition of done.

## Trigger Matrix

| Trigger | Required context | Path |
| --- | --- | --- |
| "Merge `feature/foo` into the current branch" | repo path + source ref | Path 1 + Path 2 |
| "Check whether this merge missed anything" | repo path + source ref or merge commit | Path 1 + Path 3 |
| "How should this conflict be resolved, and can I push after resolving it" | repo path + conflicted files + source ref | Path 1 + Path 2 |
| "The corresponding branches in these repos all need merging; help me confirm whether it is correct" | repo list + source refs | Path 1 + Path 2 |
| "This branch looks already merged; help me prove whether it is really included" | repo path + source ref or merge commit | Path 3 |
| "Review this merge request before we merge it" | merge request link or id | resolve to refs first, then Path 1 + Path 2 |

A merge request link is a pointer, not a ref pair. Resolve it before any path runs:
read the request's source branch, target branch, and current head sha from the
forge (the `gitlab` skill or `glab`/`gh` when available), then restate them as the
source ref and target branch this review is actually about, and confirm the local
repo has both fetched. A request retargeted or force-pushed since it was opened
still shows its original title — trust the head sha you just read, not the link.

## Context Sources

Path 1 collects the repo scope, worktree state, and merge evidence step by step. Before starting, scan instead for the boundaries that change how those steps run, because each one invalidates a default the workflow would otherwise take:

- A dirty worktree, multi-repo coordination, submodules, binary files, or large numbers of renames — none of these are handled by a plain diff model
- The repo's history strategy (fast-forward, merge commit, squash, or a rewritten history) — it decides which completeness proof is even valid
- Whether a networked `fetch` is required, and whether it is available

Environment prerequisites: a working git CLI with read access for modeling or auditing, and write access only for Path 2; judging a remote source ref usually requires a networked `fetch`.

## Bundled Resources

Load these on demand instead of cramming every detail into the main flow:

- When you need command templates, the strategy matrix, patch-equivalent, or completeness-verification methods, read [references/merge-workflow.md](references/merge-workflow.md)
- When you need to judge hotspot risk, conflict semantics, or post-merge logical-mismatch patterns, read [references/merge-review-checklist.md](references/merge-review-checklist.md)
- When you need a stable reporting skeleton, run [scripts/build_merge_evidence.py](scripts/build_merge_evidence.py) after the refs are locked down and the risks identified, to avoid evidence drift from hand-assembling the Reporting fields each time. For its flags and its unfilled-marker behavior, read [references/merge-workflow.md](references/merge-workflow.md) section 9, "Reporting skeleton".

## Workflow Paths

### Path 1: Model the diff and decide the merge plan

1. Stabilize the worktree.
   - First check `git status --short --branch`
   - Confirm the actual branch and worktree with `git rev-parse --abbrev-ref HEAD` + `git worktree list`; do not rely on a shell prompt or statusline (it can be stale or wrong). When the user named a target branch or worktree, assert HEAD matches it before editing or pushing — if it does not, stop and correct, rather than acting on the wrong line.
   - A dirty worktree is not merged directly by default; first state the risk, then decide whether to continue
2. Lock down the source and target refs.
   - Clarify the source ref, the remote, and the target branch (normally the current branch you merge into)
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
   - Any commit this path lands (merge commit or conflict-resolution commit) must not carry AI/agent provenance in its message — no attribution, generation disclosure, tool/model name, or signature marker such as `Co-Authored-By: Claude`, `Generated with Claude Code`, or `🤖`; strip any such line a global default, template, or harness convention injects before committing; the same goes for content you author while resolving conflicts — do not introduce AI-provenance comments or markers into the resolved files
2. Resolve conflicts using three-way evidence.
   - For each conflicted file, look at base / ours / theirs
   - Record the final resolution and why no necessary semantics from the other side were lost
3. Prove "complete merge".
   - Prove the source ref is included in `HEAD`
   - Prove `HEAD..<source-ref>` is empty
   - For a squash merge, `is-ancestor` does not apply; choose an alternative proof method per [references/merge-workflow.md](references/merge-workflow.md) section 7.5, "Squash merge completeness verification", and annotate `proof-method`
   - List the files and diffs that actually landed
4. Do another post-merge semantic re-review.
   - Check whether the final code is just one side's logic winning by mistake
   - Focus on shared boundaries, initialization chains, configuration closure, default resources, and upstream/downstream repo coordination
5. Run the minimal relevant verification.
   - Run only the verification commands that could actually fail because of this merge
   - In multi-repo scenarios, record per repo; do not collapse into a single "all passed"
   - When the diff's own updated tests only assert configuration shape (counts, JSON structure) and never exercise the runtime, disk, or external state where this merge could actually fail, a green run is not evidence — trace the downstream consumer's code path and simulate the post-merge pipeline (for example a re-pin / `bump` / `apply` against the tracked ref) by reading it
6. Decide whether to allow a push.
   - Push only when the user explicitly requests it or the process explicitly requires it
   - When the change registers or references an externally-sourced artifact (a skill, package, submodule pin, generated asset), gate the merge on that artifact already being published on the exact ref the config tracks (`git ls-remote` the tracked branch), not merely present in a local unpushed commit — otherwise the post-merge pipeline resolves the tracked ref and hard-fails on the missing artifact
   - If any gate is skipped, you must explicitly state the reason and the residual risk

### Path 3: Audit a completed merge

1. Lock down the audit target.
   - Clarify whether you are auditing a specific merge commit, a specific source ref, or the current worktree result
2. Reconstruct the expected diff.
   - Recompute the merge base, incoming commits, file sets, and hotspot overlap
   - Do not equate "there is no diff now" with "it was merged correctly back then"
   - On parallel/independent baseline lines, the same logical change often lands via a **different commit and issue id** on each line; `is-ancestor <sha>`, a commit-id search, and an issue-number search can all report "missing" while the content is actually present. Judge "does this branch contain the fix" by the **file content / patch**, not the commit graph or issue id (see [references/merge-workflow.md](references/merge-workflow.md) section 3.4, "Parallel baseline lines").
3. Check completeness and semantics.
   - Cross-check the source ref, the landed files, and the final code
   - Focus on the post-merge error patterns in [references/merge-review-checklist.md](references/merge-review-checklist.md)
4. Run the minimal relevant verification and produce a conclusion.
   - The conclusion can only be `Green / Yellow / Red`
   - It must come with an evidence matrix and residual risks

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
- dirty worktree status:
- merge strategy:
- conflicted files and reasoning:
- completeness proof:
- proof method: (is-ancestor | patch-equivalent | tree-diff | cherry-pick-noop)
- semantic review conclusion:
- verification command(s):
- push status:
- residual risks:

For a multi-repo scenario, report per repo; do not substitute a single "all merged fine".
