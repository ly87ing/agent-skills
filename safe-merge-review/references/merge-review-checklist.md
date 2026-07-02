# Merge Review Checklist

## Table of Contents

- 1. When to use
- 2. Mandatory pre-merge review
- 3. Conflict-resolution review
- 4. Post-merge logical-error patterns
- 5. Multi-repo coordination review
- 6. Completeness and wrap-up
- 7. Evidence-matrix template

## 1. When to use

Use this checklist twice:

- Before the merge: decide whether it is worth merging directly, or whether you must first deep-read the hotspot logic
- After the merge: decide whether the final result is "Git succeeded but the logic is mismatched"

## 2. Mandatory pre-merge review

### 2.1 Worktree and scope

- Is the current repo clean?
- Are there still uncommitted user changes that would contaminate the merge evidence?
- Does the request cover multiple repos? If so, has it already been split per repo?

### 2.2 Diff scope

- Is the merge base clear?
- Do the incoming commits really need to enter the current branch?
- Are there patch-equivalent commits that, after rebase/squash, look like they were "not merged"?

### 2.3 Hotspot overlap

If any of the following is "yes", flag the file as high-risk:

- Both sides changed the same file
- Both sides changed the same class, the same method, or the same config key
- The change lands in a shared util / adapter / base service
- The change touches a public interface, DTO, or API contract
- The change touches schema, migration, initialization, backfill, or rollback
- The change touches build, packaging, deploy, or CI
- The change touches tests, fixtures, mocks, or snapshots

### 2.4 Semantic issues

For each high-risk file, answer at least:

- What does the current branch want to preserve here?
- What did the source branch add or fix here?
- Should the final result be additive, pick one side, or be rewritten?
- If you simply keep ours or theirs, would you lose semantics the other side truly needs?

### 2.5 New modes / types / config

When the source branch adds the following, check the closure item by item:

- New modes, new switches, new schema keys
- New database types, new deployment types, new runtime modes
- New services, new modules, new resource files
- New config-center entries, new defaults, new templates

You must ask:

- Are the default resources synchronized?
- Is the initialization logic synchronized?
- Is the validation logic synchronized?
- Is the liveness logic synchronized?
- Is the rollback/recovery logic synchronized?
- Are the tests synchronized?

## 3. Conflict-resolution review

For each conflicted file, record:

- The old behavior in base
- The intent of the change in ours
- The intent of the change in theirs
- The final resolution
- Why this resolution does not lose the necessary logic of the other side

Common mistakes:

- Keeping only the text inside the conflict block, but not the accompanying import / registration / test
- Merging the method body, but not following up on the callers, config entries, and defaults
- Compiles after resolving the conflict, but the runtime conditional branch is already distorted

## 4. Post-merge logical-error patterns

After the merge, focus on the following patterns:

### 4.1 The outer condition is generalized, but the inner implementation still hardcodes the old branch

Typical signs:

- The outer condition changes from `if ("distribute")` to `if (clusterDeploy)`
- But internally it still hardcodes the old mode, old service name, old config key

### 4.2 New mode support is added, but the default resources are not filled in

Typical signs:

- The code now supports a new mode, new template, new database type
- But the default JSON / YAML / ConfigMap / assets / template are not synchronized

### 4.3 The entry point accepts a new type, but the initialization chain is incomplete

Typical signs:

- The controller / service accepts the new type
- But initialization, backfill, liveness, state sync, recovery, and monitoring still support only the old type

### 4.4 Only the "deploy action" was merged, not the "config closure"

Typical signs:

- You can create resources, start Pods, send requests
- But the key config is not written back to system state or the config center

### 4.5 The companion repo or an upstream/downstream repo is not synchronized

Typical signs:

- The backend contract changed, but the frontend did not follow
- The admin side changed the flow, but the infrastructure repo did not follow
- One repo is `Already up to date`, but another repo genuinely has changes, yet in the end it is still wrongly reported under a unified statement

### 4.6 Tests and the safety net are weakened

Typical signs:

- Tests are deleted, downgraded, or skipped
- The build gate, validation scripts, or packaging guards are removed
- The smoke test no longer covers the real risk

## 5. Multi-repo coordination review

If the current request involves "frontend and backend", "main repo + companion repo", or "multiple independent repos", review per repo:

- Whether the current branch names are consistent
- Whether the source branch names are consistent
- Which repos genuinely have incoming commits
- Which repos are merely up-to-date
- Which repos need a merge, and which repos should not create an empty merge commit
- The final conclusion must be reported per repo; it cannot be glossed over with a single "all merged fine"

## 6. Completeness and wrap-up

After the merge, confirm at least once more:

- The source ref is already an ancestor of `HEAD`
- `HEAD..<source-ref>` is empty
- For a squash merge, `is-ancestor` does not apply; you must verify with patch-equivalent, tree-diff, or a cherry-pick no-op, and annotate `proof-method` in the evidence
- The actually-landed files match the expected files
- No conflict markers remain
- No case of "thought it was merged but it did not actually land on the working branch"
- The minimal relevant verification has been executed
- If it is not verified, has that been clearly stated?

## 7. Evidence-matrix template

Use the template below to produce the final conclusion:

| Item | Content |
| --- | --- |
| Repo | |
| Current branch | |
| Source ref | |
| Merge base | |
| Left/right counts | |
| Incoming key commits | |
| Hotspot overlap files | |
| Dirty worktree status | |
| Merge strategy | |
| Conflicted files | |
| Completeness proof | |
| Proof method | is-ancestor / patch-equivalent / tree-diff / cherry-pick-noop |
| Semantic review conclusion | |
| Verification command(s) | |
| Push status | |
| Residual risks | |

Suggested verdict rules:

- `Green`: completeness passes, semantic re-review passes, verification passes
- `Yellow`: the merge is complete, but there are skipped items or residual risk
- `Red`: there is a missed merge, logical mismatch, unresolved conflict, or verification failure
