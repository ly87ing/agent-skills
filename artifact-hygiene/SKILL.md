---
name: artifact-hygiene
description: Decide safe locations, redaction, and cleanup rules for generated files, debug output, Playwright traces/screenshots/videos, downloaded artifacts, temporary scripts, backup or timestamped duplicate copies of files already under version control, reports, storage state, JSON/HTML dumps, workflow-consumed outputs, and requested deliverables the user asked to produce. Also covers keeping plaintext secrets and credentials out of printed command output and logs, and restoring low-privilege credentials after a temporary elevation. Use before creating or keeping such artifacts, when packaging a deliverable for handover to another person or machine, or when deciding where a file the user asked for should live — to avoid polluting a repository, committing something by accident, shipping customer or personal data baked into a screenshot or recording, or stranding a deliverable in a throwaway location. Also covers repository weight from committed binaries and media, and destructive git history rewriting.
---

# Artifact Hygiene

## Classify Outputs

- **Requested deliverables:** files the user explicitly asked you to produce as the end product — a deck, document, export, or report they intend to keep and use. Classified by *why they exist*, not their file format: an HTML deck you were told to "make" is a deliverable, not a "dump."
- **Project assets:** maintained source code, shared helpers, stable fixtures, maintained config, approved snapshots, and durable docs.
- **Workflow-consumed artifacts:** generated files that repository workflows already depend on, or outputs the user explicitly asks to standardize.
- **Disposable run artifacts:** ad hoc debug scripts, copied reports, temporary screenshots, traces, videos, downloads, storage state, JSON/HTML dumps, and investigation notes serving only the current run.

## Placement Rules

1. Put requested deliverables where their peers already live — the maintained knowledge-base/project path a reader would look for them. If there is no clear peer or path, ask the user where it belongs instead of defaulting to a temporary/scratchpad directory. Never treat a requested deliverable as disposable, and do not delete it on completion. A session-level "put temporary files in the scratchpad" instruction does not override this — it governs disposable run artifacts, not a deliverable the user asked you to produce; when the two seem to conflict, the deliverable's placement wins. Once a deliverable lands in its maintained path, that file is the only copy: edit it in place rather than keeping a scratchpad duplicate to sync over, which drifts and invites edits to the wrong file.
2. Put project assets in the maintained project path.
3. Put workflow-consumed artifacts in the project's existing gitignored output path.
4. Put disposable artifacts in `mktemp -d`, `$TMPDIR`, or `/tmp` unless a working-tree path is required.
5. When you cannot immediately tell whether an artifact is disposable or worth keeping, apply the reuse test: would a future run, a teammate, or a fresh machine need it again (a config, an automation/bootstrap script, a reusable fixture)? If yes it is a project asset (rule 2); if it only serves the current run it is disposable (rule 4). If it is still genuinely ambiguous, ask the user; if you cannot ask (a non-interactive or CI run), fall back to treating it as disposable rather than writing it into the working tree.
6. Delete temporary project-local artifacts before completion unless the user asks to keep them.

## Playwright Defaults

- Treat test specs, page objects, shared fixtures, helper utilities, stable config changes, and intentional snapshots as project assets.
- Treat `playwright-report/`, `test-results/`, `blob-report/`, and JUnit/JSON outputs as workflow-consumed only when project workflows use them.
- Treat one-off traces, videos, screenshots, downloads, copied reports, temporary auth state, and ad hoc HAR/JSON/storage dumps as disposable.

## Sensitive Content In Shipped Artifacts

- Before source material — a screenshot, an exported report, a recording, a real internal document — enters a reader-facing artifact or version control, mask third-party and personal identifiers: customer or account names, monetary amounts, contact details, individual names, and internal hosts or addresses. Real material is the strongest evidence, but only the redacted version may travel.
- Set the redaction bar by the artifact's real audience and destination, not by reflex: the rule above is calibrated to an external, shipped, or shared-version-control destination. For an internal-only audience the real, unredacted evidence is legitimate and more convincing, and over-redacting there costs the credibility the evidence was meant to carry. Genuine secrets — credentials, tokens, keys — stay out regardless of audience. When one internal run needs the unredacted form, make it a per-run exception rather than weakening a reusable redaction or scanning gate that other runs still depend on.
- Keep the unredacted original out of version control, and never tell the reader to copy a whole asset directory that also holds unredacted originals — name the redacted files to take.
- A redaction or secret-scanning gate that reads only text formats is blind to what is baked into images, video, and other binaries. Either scan rendered frames and pixels too, or state plainly that the gate does not cover them — reporting a clean pass over content it never inspected is worse than running no gate at all.
- Keep plaintext credentials out of live command output and logs, not just out of files: `cat`-ing an inventory or config that embeds passwords prints them into the session transcript, so mask secrets before printing (`***`) and read specific keys instead of dumping the file. After a temporary privilege elevation (an admin token, a high-privilege key), restore the everyday low-privilege credential as soon as the privileged step is done and remind the user to revoke the temporary one — never leave the elevated credential as the new default.

## Shareable Deliverables

- Keep a deliverable and every asset it loads at runtime inside one self-contained folder, and keep drafts, notes, and source material in a separately named subfolder the export step excludes — a handover that needs manual pruning gets pruned wrong.
- Register each machine-local or gitignored asset in the deliverable's own dependency checklist as you add it, so the deliverable still works when it is opened on another machine.
- Prove shareability by copying the export to a clean location and opening it there; a reference that only resolves on the authoring machine is a broken deliverable.
- When the user supplies an image or file from an application's temporary directory (a chat client's cache, a download staging path), copy it into the deliverable's own asset directory before referencing it — those directories get cleaned and the reference breaks silently.

## Hard Boundaries

- Do not create or widen `.gitignore`, config conventions, or repository directories just to host disposable outputs.
- Do not invent a project-local output convention unless the user explicitly asks for a reusable convention.
- Never place disposable artifacts in tracked or likely-to-be-committed paths such as repo root, `docs/`, `scripts/`, `tests/fixtures/`, or ad hoc folders.
- When a file is already under version control (git etc.), do not create `.bak`, backup, or timestamped duplicate copies of it before editing — history already preserves the prior state, so such copies are disposable clutter. Without version control, a pre-edit backup can be legitimate. If a *feature* needs to snapshot data (e.g. a pre-upgrade config backup), make it opt-in and default-off rather than always producing copies.

## Repository Weight From Binaries

- In a repo that also stores binaries or media (a knowledge base, an Obsidian-style vault, an assets tree), gitignore the media so it never enters history — deleting a committed binary from the working tree does not reclaim the space it already took in `.git`.
- When `.git` is already heavy, diagnose the actual large objects before rewriting (`git filter-repo --analyze`, or `git rev-list --objects --all` with `git cat-file --batch-check` sorted by size) rather than assuming the biggest current file is the cause — the real weight is usually old binaries already deleted from the tree, while the file you suspected may have been ignored all along.
- History rewriting (`git filter-repo`) is destructive and changes every later commit hash: take a `git bundle` backup first, confirm the diagnosed objects, then coordinate the force-push with anyone sharing the repo. This pre-rewrite bundle is a deliberate safety net, not the per-file `.bak` clutter the hard boundary forbids.
