---
name: safe-merge-review
description: Use when the user wants to merge a branch, a remote ref, or the corresponding branches across a set of related repos into the current working branch, or wants to review whether "is this branch ready to merge", "this merge is correct", "anything was missed", "the conflict resolution is reliable", or "it is safe to push after the merge". Applies when the user provides a branch name, remote ref, repo path, conflicted files, a merge commit, a merge request link, or a multi-repo set of branches; also when confirming a fix is really present on a parallel release line that commit-id or is-ancestor searches report as missing, and when a merge decision turns on another repo's dependency not yet on the tracked ref. Proves the merge is correct, not merely that git merge ran. Not for branch code-quality review while no merge, audit, or conflict is in play.
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
| "Is this branch ready to merge into main?" | repo path + source ref + target branch | Path 4 |
| "Review this merge request before we merge it" | merge request link or id | resolve to refs first, then Path 4 |

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
- After the refs are locked down, run [scripts/build_merge_evidence.py](scripts/build_merge_evidence.py) with `--collect --repo <path> --source-ref <ref>` (add `--target-ref <ref>` when the target is not the checked-out branch) to derive the read-only Git facts and a stable reporting skeleton in one bounded output. For the post-merge re-run, manual fields, and unfilled-marker behavior, read [references/merge-workflow.md](references/merge-workflow.md) section 9, "Reporting skeleton".

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
   - Fetch the locked source ref, then use the evidence script's `--collect` mode for merge base, left/right counts, incoming commits, and hotspot intersection; inspect its residual-risk line if a long list was truncated
   - When the history shows signs of rebase / squash / rewrite, additionally run the patch-equivalent check
4. Identify the hotspot overlap and do a semantic pre-review.
   - Rank the hotspot files the script lists by the high-risk signs in [references/merge-review-checklist.md](references/merge-review-checklist.md) section 2.3, and review the high-risk ones item by item per its sections 2.4 and 2.5
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
   - Re-run the evidence script's `--collect` mode with `--pre-merge-ref` set to the target as it was before the merge (`HEAD^1` for a merge commit, the sha saved before a fast-forward or squash): the diff model stays computed against the old target, completeness is proved against the final `HEAD`, and the landed files are listed. Without it, the merge base becomes the source tip and the incoming and hotspot lists come back `none`
   - Prove the source ref is included in `HEAD`
   - Prove `HEAD..<source-ref>` is empty
   - For a squash merge, `is-ancestor` does not apply; choose an alternative proof method per [references/merge-workflow.md](references/merge-workflow.md) section 7.5, "Squash merge completeness verification", and annotate `proof-method`
   - List the files and diffs that actually landed
4. Do another post-merge semantic re-review.
   - Check whether the final code is just one side's logic winning by mistake
   - Focus on shared boundaries, initialization chains, configuration closure, default resources, and upstream/downstream repo coordination
5. Run the minimal relevant verification.
   - When the diff's own updated tests only assert configuration shape (counts, JSON structure) and never exercise the runtime, disk, or external state where this merge could actually fail, a green run is not evidence — trace the downstream consumer's code path and simulate the post-merge pipeline (for example a re-pin, `bump`, or `apply`) by reading it
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

### Path 4: Judge readiness without merging

1. Lock down the source ref and the target branch as in Path 1 step 2, fetch both, and model the diff with the evidence script's `--target-ref <target-ref>`; the user's checked-out branch does not have to be the target, and its dirty state does not block a trial merge that never touches it.
2. Trial-merge in a disposable worktree per [references/merge-workflow.md](references/merge-workflow.md) section 5.4, never in the user's worktree; read the conflicts and staged result there, and run the minimal relevant verification there.
3. Review the hotspots and the conflicts semantically, as in Path 1 step 4 and Path 2 step 2, without writing a resolution.
4. Remove the trial worktree, then report `Green / Yellow / Red` with the merge decision: merge as is, merge after named fixes, or do not merge. Commit, merge, and push nothing; Path 2 runs only when the user asks for the merge.

## Failure and Escalation

Stop or escalate, instead of continuing to guess, when:

- The source ref, target ref, or remote is unclear
- A dirty worktree would contaminate the merge evidence, but the user has not yet confirmed a handling strategy
- You cannot `fetch` the latest source state but still need to judge a remote branch
- A destructive action is required (such as `reset`, `checkout --`, or force-overwriting the conflict result), but the user has not yet approved it
- In a multi-repo coordination, some repo lacks context, lacks a source ref, or lacks a verification command

## Reporting

After completing, report at least the following:

### Safe merge review summary

The skeleton and field order come from [scripts/build_merge_evidence.py](scripts/build_merge_evidence.py); what each field means:

- repo: the repository under review
- target: the branch the source merges into — the checked-out branch, or the ref given with `--target-ref`
- source ref: the exact ref being merged in
- merge base: the common ancestor all diff modeling is based on
- left/right counts: commits exclusive to each side
- incoming key commits: the source-side commits that matter semantically
- hotspot overlap files: files both sides changed since the merge base
- landed files: files the merge actually changed on the target (collected with `--pre-merge-ref`)
- dirty worktree status: worktree state and how it was handled
- merge strategy: already-contained / fast-forward / no-ff / squash, and why
- conflicted files and reasoning: each conflict and why the resolution loses no needed semantics
- completeness proof: the evidence that the source landed fully
- proof method: (is-ancestor | patch-equivalent | tree-diff | cherry-pick-noop)
- semantic review conclusion: result of the post-merge semantic re-review
- verification command(s): the minimal relevant verification actually run
- push status: pushed / not pushed, and the gate decision
- residual risks: anything skipped, unverified, or still risky

For a multi-repo scenario, report per repo; do not substitute a single "all merged fine".
