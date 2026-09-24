---
name: artifact-hygiene
description: Decide safe locations, redaction, and cleanup rules for generated files, debug output, Playwright traces/screenshots/videos, downloads, temporary scripts, backup or timestamped copies of tracked files, reports, storage state, JSON/HTML dumps, workflow-consumed outputs, and deliverables the user asked to produce. Also covers keeping plaintext secrets and credentials out of printed command output and logs — and restoring a low-privilege credential after a temporary elevation. Use before creating or keeping such artifacts, when packaging a deliverable for handover to another person or machine, or when a requested file has no obvious home — to avoid a polluted repository, an accidental commit, personal data baked into a screenshot or recording, or a stranded deliverable. Also covers repository weight from committed binaries and media, and destructive git history rewriting.
---

# Artifact Hygiene

## Classify Outputs

- **Requested deliverables:** files the user explicitly asked you to produce as the end product — a deck, document, export, or report they intend to keep and use. Classified by *why they exist*, not their file format: an HTML deck you were told to "make" is a deliverable, not a "dump."
- **Project assets:** maintained source code, shared helpers, stable fixtures, maintained config, approved snapshots, and durable docs.
- **Workflow-consumed artifacts:** generated files that repository workflows already depend on, or outputs the user explicitly asks to standardize.
- **Handed-over evidence:** a test upload, a probe file, or a screenshot the user or a downstream consumer will look at to confirm a result. It stays until that confirmation arrives; cleaning it up early turns the evidence into a false alarm on their side.
- **Disposable run artifacts:** ad hoc debug scripts, copied reports, temporary screenshots, traces, videos, downloads, storage state, JSON/HTML dumps, and investigation notes serving only the current run.

## Ownership Boundary

This skill owns an artifact's placement, redaction, dependency packaging, cleanup, and
handoff. It does not decide what a reader-facing artifact should say, model or lay out
a technical diagram, or prove a rendered interface in a browser. When available, use
`reader-facing-writing`, `technical-diagramming`, and `verification` for those
decisions; they may run alongside this skill without becoming prerequisites for its
artifact-lifecycle work.

## Placement Rules

1. Put requested deliverables where their peers already live — the maintained knowledge-base/project path a reader would look for them. If there is no clear peer or path, ask the user where it belongs instead of defaulting to a temporary/scratchpad directory. Never treat a requested deliverable as disposable, and do not delete it on completion. A session-level "put temporary files in the scratchpad" instruction does not override this, because it governs disposable run artifacts, not requested deliverables. Once a deliverable lands in its maintained path, that file is the only copy: edit it in place rather than keeping a scratchpad duplicate to sync over, which drifts and invites edits to the wrong file.
2. Put project assets in the maintained project path.
3. Put workflow-consumed artifacts in the project's existing gitignored output path.
4. Put disposable artifacts in the scratchpad or temporary directory the runtime provides; when it provides none, in a fresh `mktemp -d`, which honours `$TMPDIR`. Never write them to a fixed name directly under `/tmp`, where another run can collide with or read them. Use a working-tree path only when a tool requires one, and delete it per rule 6.
5. When you cannot immediately tell whether an artifact is disposable or worth keeping, apply the reuse test: would a future run, a teammate, or a fresh machine need it again (a config, an automation/bootstrap script, a reusable fixture)? If yes it is a project asset (rule 2); if it only serves the current run it is disposable (rule 4). If it is still genuinely ambiguous, ask the user; if you cannot ask (a non-interactive or CI run), fall back to treating it as disposable rather than writing it into the working tree.
6. Delete temporary project-local artifacts before completion unless the user asks to keep them; handed-over evidence waits for the consumer's confirmation first.

## Playwright Defaults

- Treat test specs, page objects, shared fixtures, helper utilities, stable config changes, and intentional snapshots as project assets.
- Treat `playwright-report/`, `test-results/`, `blob-report/`, and JUnit/JSON outputs as workflow-consumed only when project workflows use them.
- Treat one-off traces, videos, screenshots, downloads, copied reports, temporary auth state, and ad hoc HAR/JSON/storage dumps as disposable.

## Sensitive Content In Shipped Artifacts

- Set the redaction bar by the widest reader the destination will ever have. Before source material — a screenshot, an exported report, a recording, a real internal document — goes where someone not entitled to it can read it (an external reader, a customer delivery, a public or broadly shared repository), mask third-party and personal identifiers: customer or account names, monetary amounts, contact details, individual names, and internal hosts or addresses. Real material is the strongest evidence, but only the redacted version travels there.
- An internal destination is one whose every reader is entitled to the material, and that includes a repository: a team's internal knowledge-base repository may hold the real screenshot, and over-redacting there costs the credibility the evidence was meant to carry. Judge a repository by its readers over time, not today — a commit stays in every clone, so a repository that may be opened up, mirrored outward, or handed to a vendor is already external. Genuine secrets — credentials, tokens, keys — stay out of every destination regardless. When one internal run needs the unredacted form, make it a per-run exception rather than weakening a reusable redaction or scanning gate that other runs still depend on.
- When both forms exist, the unredacted original goes only to destinations whose readers are entitled to it; never tell the reader to copy a whole asset directory that also holds originals — name the redacted files to take.
- A redaction or secret-scanning gate that reads only text formats is blind to what is baked into images, video, and other binaries. Either scan rendered frames and pixels too, or state plainly that the gate does not cover them — reporting a clean pass over content it never inspected is worse than running no gate at all.
- Keep plaintext credentials out of live command output and logs, not just out of files: `cat`-ing an inventory or config that embeds passwords prints them into the session transcript, so mask secrets before printing (`***`) and read specific keys instead of dumping the file. After a temporary privilege elevation (an admin token, a high-privilege key), restore the everyday low-privilege credential as soon as the privileged step is done and remind the user to revoke the temporary one — never leave the elevated credential as the new default.
- A user's password is one-shot input, never persisted: take it interactively, exchange it for the long-lived token or session the workflow needs, write only that, and confirm the password left no file, history, or log behind. Case: a login helper stored the account password in a dotenv file for a future re-login; the token it had already obtained was valid for months, so the password served one rare event at the cost of a permanent plaintext secret.

## Shareable Deliverables

- Keep a deliverable and every asset it loads at runtime inside one self-contained folder, and keep drafts, notes, and source material in a separately named subfolder the export step excludes — a handover that needs manual pruning gets pruned wrong.
- Register each machine-local or gitignored asset in the deliverable's own dependency checklist as you add it, so the deliverable still works when it is opened on another machine.
- Prove shareability by copying the export to a clean location and opening it there; a reference that only resolves on the authoring machine is a broken deliverable.
- When the user supplies an image or file from an application's temporary directory (a chat client's cache, a download staging path), copy it into the deliverable's own asset directory before referencing it — those directories get cleaned and the reference breaks silently.

## Hard Boundaries

- Do not create or widen `.gitignore`, config conventions, or repository directories just to host disposable outputs.
- Do not invent a project-local output convention unless the user explicitly asks for a reusable convention.
- Never place disposable artifacts in tracked or likely-to-be-committed paths.
- When a file is already under version control (git etc.), do not create `.bak`, backup, or timestamped duplicate copies of it before editing — history already preserves the prior state, so such copies are disposable clutter. Without version control, a pre-edit backup can be legitimate.

## Repository Weight From Binaries

- Classify binaries and media by role, not file type. Keep required, reviewable product or documentation assets under the repository's existing versioning or large-file policy; ignore or store elsewhere the generated, disposable, sensitive, or oversized media that does not belong in source history. Do not add a broad media ignore pattern that also hides maintained assets. Deleting a committed binary from the working tree does not reclaim the space it already took in `.git`.

History rewriting is destructive and changes every later commit hash. Run it only in this order:

1. Diagnose the actual large objects (`git filter-repo --analyze`, or `git rev-list --objects --all` with `git cat-file --batch-check` sorted by size) rather than assuming the biggest current file is the cause — the real weight is usually old binaries already deleted from the tree, while the file you suspected may have been ignored all along.
2. Take a backup outside the repository with `git bundle create <path> --all` and check it with `git bundle verify <path>`. This bundle is a deliberate safety net, not the per-file `.bak` clutter the hard boundary forbids.
3. Show the user the objects and paths the rewrite will remove, and wait for an explicit go-ahead.
4. Rewrite with `git filter-repo`, naming exactly the diagnosed paths or objects.
5. Re-run the step 1 diagnosis and confirm the weight is gone and nothing else left.
6. Agree the force-push with everyone who shares the repository before pushing: every existing clone has to re-clone or hard-reset, and an old clone pushed back restores what was removed.

## Report

One line per artifact produced, moved, or removed in the task, and one line for anything left behind:

```text
<path> | <class> | <kept at its path, deleted, or handed over awaiting confirmation> | <redaction: not needed for this audience, applied (what), or not covered (which binaries)>
left behind: <paths and why, or none>
```
