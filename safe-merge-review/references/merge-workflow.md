# Merge Workflow

## Table of Contents

- 1. Repo scope and worktree cleanliness
- 2. Lock down the ref and fetch the latest state
- 3. Diff modeling and patch-equivalent check
- 4. Hotspot-overlap file identification
- 5. Merge strategy matrix
- 6. Conflict handling
- 7. Merge completeness verification
- 8. Minimal relevant verification and push decision

## 1. Repo scope and worktree cleanliness

For a single repo, first confirm the current directory really is a git repo. For multiple repos, first identify which repos this request covers, then run the same flow per repo.

Basic commands:

```bash
git status --short --branch
git branch --show-current
git remote -v
```

Dirty-worktree handling principles:

- `status` clean: continue.
- `status` not clean and related to this merge: stop by default, and confirm an isolation strategy with the user first.
- `status` not clean but seemingly unrelated: still state the risk first, then decide whether to continue.
- Do not silently stash, reset, or checkout over the user's existing changes.

If you need to judge whether the dirty content is related to the merge, first look at:

```bash
git diff --stat
git diff --cached --stat
```

## 2. Lock down the ref and fetch the latest state

Do not use vague descriptions such as "the latest master" or "that remote line". Lock down the precise ref first.

Common commands:

```bash
git fetch origin <source-branch>
git rev-parse HEAD
git rev-parse <source-ref>
git rev-parse --abbrev-ref HEAD
```

If the request is "merge the remote branch into the current branch", you usually first run:

```bash
git fetch origin <source-branch>
```

Then use `origin/<source-branch>` as the source ref, rather than a stale local branch name.

## 3. Diff modeling and patch-equivalent check

### 3.1 merge base

First find the common ancestor:

```bash
git merge-base HEAD <source-ref>
```

This result is the baseline for all subsequent judgments of "who is ahead, who is behind, which files overlap".

### 3.2 Left/right exclusive commit counts

```bash
git rev-list --left-right --count HEAD...<source-ref>
```

Explanation:

- Left column: the number of commits exclusive to the current branch relative to the source branch
- Right column: the number of commits exclusive to the source branch relative to the current branch

### 3.3 incoming commits

First see which commits the source branch genuinely added:

```bash
git log --oneline HEAD..<source-ref>
```

Then check whether the two sides' patches already exist equivalently:

```bash
git log --oneline --left-right --cherry-pick --no-merges HEAD...<source-ref>
```

When the source branch has been through rebase, squash, or history rewrite, additionally run:

```bash
git range-diff "$(git merge-base HEAD <source-ref>)"..HEAD "$(git merge-base HEAD <source-ref>)"..<source-ref>
```

Only after running the patch-equivalent check may you interpret "the commit does not exist" as "it was really not merged in".

### 3.4 Parallel baseline lines: same fix, different commit

On products that cut independent per-version / per-customer baseline branches, the same logical change is frequently merged into each line by a **different commit with a different issue id** (each line raises its own ticket). Consequences:

- `git merge-base --is-ancestor <specific-sha> <branch>` returns false even though the content is present.
- Searching by the original commit id or issue number finds nothing on the other line.
- The lines may share no merge base at all (`git merge-base` empty), so ancestry checks are meaningless.

Therefore, to decide "does branch X contain fix Y", compare the **actual file content / patch**, not the commit graph:

```bash
git show <branch>:<path-to-file> | grep -n "<the fix's distinguishing content>"
# or diff the final state on the changed paths against a known-fixed ref:
git diff <branch> <known-fixed-ref> -- <path>
```

Only conclude "not fixed on this line" when the content is genuinely absent. To port the fix, do not blindly `cherry-pick <sha>` — the target line may not even carry the same file/baseline; confirm the target's structure first.

## 4. Hotspot-overlap file identification

First list, for each side separately, the files changed since the merge base:

```bash
BASE=$(git merge-base HEAD <source-ref>)
git diff --name-only "$BASE"..HEAD
git diff --name-only "$BASE"..<source-ref>
```

Then take the intersection, and focus on the files both sides changed.

If the shell environment allows, you can use:

```bash
BASE=$(git merge-base HEAD <source-ref>)
git diff --name-only "$BASE"..HEAD | sort -u > /tmp/current.files
git diff --name-only "$BASE"..<source-ref> | sort -u > /tmp/source.files
comm -12 /tmp/current.files /tmp/source.files
```

Prioritize reviewing the following overlaps:

- Shared service / util / adapter
- controller and API contract
- Config, schema, migration, initialization logic
- build, packaging, deploy, CI scripts
- Tests and test fixtures
- Generated artifacts and their source files

## 5. Merge strategy matrix

### 5.1 The source is already fully included in the current branch

If:

```bash
git merge-base --is-ancestor <source-ref> HEAD
```

returns success, the source is already included. Do not run a merge; report `Already contained / up to date` directly.

### 5.2 The current branch is an ancestor of the source branch

If:

```bash
git merge-base --is-ancestor HEAD <source-ref>
```

returns success, this is a fast-forward candidate.

Recommended flow:

1. First complete incoming commits, the file list, and the semantic review.
2. Then choose one of two based on the repo's history strategy:

```bash
git merge --ff-only <source-ref>
```

or

```bash
git merge --no-ff --no-commit <source-ref>
```

If you need to preserve explicit merge evidence or inspect the staged result first, prefer the second.

### 5.3 A genuinely non-trivial merge

By default first use:

```bash
git merge --no-ff --no-commit <source-ref>
```

First inspect the staged result:

```bash
git diff --cached --stat
git diff --cached --name-only
git diff --cached
```

After confirming the result is correct, create the final merge commit.

Do not treat `git merge --no-edit <source-ref>` as the default path, unless you have already proven this is a low-risk, low-ambiguity trivial merge.

## 6. Conflict handling

When a conflict occurs, first locate the files:

```bash
git diff --name-only --diff-filter=U
git ls-files -u
```

Then look at the three-way content separately:

```bash
git show :1:path/to/file
git show :2:path/to/file
git show :3:path/to/file
```

Meaning:

- `:1:` base
- `:2:` ours
- `:3:` theirs

Conflict-handling rules:

- First state what was originally in base.
- Then state what the current branch changed.
- Then state what the source branch changed.
- The final result must be able to explain why one side's logic was preserved, merged, or discarded.

After resolving, additionally check:

```bash
git diff --check
```

This finds residual conflict markers, whitespace errors, and similar issues.

## 7. Merge completeness verification

Before genuinely claiming "merged", provide at least the following evidence.

### 7.1 Merge commit or merge-result snapshot

If the merge commit is already committed:

```bash
git show --no-patch --pretty=raw HEAD
git show --stat --oneline -1
```

If still in the `--no-commit` state:

```bash
git diff --cached --stat
git diff --cached --name-only
```

### 7.2 The source ref is included

```bash
git merge-base --is-ancestor <source-ref> HEAD
```

Must succeed.

### 7.3 No remaining incoming commits

```bash
git log --oneline HEAD..<source-ref>
```

Must be empty.

### 7.4 Actually-landed files align with expected files

At least look at:

```bash
git diff --stat HEAD^1 HEAD
git diff --name-only HEAD^1 HEAD
```

Or, for a fast-forward merge, save the pre-merge commit:

```bash
PRE_MERGE_HEAD=$(git rev-parse HEAD)
git merge --ff-only <source-ref>
git diff --stat "$PRE_MERGE_HEAD"..HEAD
git diff --name-only "$PRE_MERGE_HEAD"..HEAD
```

For a multi-repo merge, do this step per repo.

### 7.5 Squash merge completeness verification

`git merge-base --is-ancestor` does not apply to a squash merge, because the original commits are not ancestors of HEAD. An alternative proof path is needed.

**Method 1: patch-equivalent check**

Verify whether all of the source branch's changes already exist equivalently in the current branch:

```bash
BASE=$(git merge-base HEAD <source-ref>)
git diff "$BASE"..<source-ref> > /tmp/source.patch
git diff "$BASE"..HEAD > /tmp/current.patch
```

If all hunks of source.patch are already contained in current.patch, the changes have been merged in equivalently.

A more precise approach is to compare the final state file by file:

```bash
git diff HEAD <source-ref> -- <hotspot-files>
```

If the diff of the hotspot files is empty or only contains follow-up changes exclusive to the current branch, the source changes have landed.

**Method 2: cherry-pick --no-commit no-op check**

```bash
git stash
git cherry-pick --no-commit <source-commits>
git diff --cached --stat
git cherry-pick --abort
git stash pop
```

If, after the cherry-pick, the staged area is empty or has only conflicts (because the changes already exist), the content is already included.

**Method 3: tree-level diff**

Directly compare the final file state of the source branch and the current branch on the key paths:

```bash
git diff HEAD <source-ref> --stat
```

Confirm file by file: the differences come only from the current branch's subsequent evolution, not from omissions on the source branch.

Verdict rules for the squash merge scenario:

- You cannot use `is-ancestor` as the sole completeness evidence
- You must use at least one of the above methods, and annotate `proof-method: patch-equivalent` or `proof-method: tree-diff` in the evidence matrix
- If the source branch still has new commits after the squash, you must recheck rather than reuse the old conclusion

## 8. Minimal relevant verification and push decision

Based on the actual changes, choose a minimal but genuinely-failable verification:

- Java code: `compileJava`, relevant unit tests, module tests
- Frontend code: relevant tests, build, local smoke
- Config/scripts: run the corresponding check or dry-run
- Multi-repo coordination: verify per repo, then give an overall result

After verifying, look once more:

```bash
git status --short --branch
```

Only when all of the following conditions hold simultaneously may you suggest or perform a push:

- The source ref is fully included
- The post-merge semantic re-review passes
- The minimal relevant verification passes
- The user requested a push, or the repo process explicitly requires continuing to push
