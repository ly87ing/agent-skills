---
name: artifact-hygiene
description: Decide safe locations and cleanup rules for generated files, debug output, Playwright traces/screenshots/videos, downloaded artifacts, temporary scripts, reports, storage state, JSON/HTML dumps, workflow-consumed outputs, and requested deliverables the user asked to produce. Use before creating or keeping such artifacts, or when deciding where a file the user asked for should live — to avoid polluting a repository, committing something by accident, or stranding a deliverable in a throwaway location.
---

# Artifact Hygiene

## Classify Outputs

- **Requested deliverables:** files the user explicitly asked you to produce as the end product — a deck, document, export, or report they intend to keep and use. Classified by *why they exist*, not their file format: an HTML deck you were told to "make" is a deliverable, not a "dump."
- **Project assets:** maintained source code, shared helpers, stable fixtures, maintained config, approved snapshots, and durable docs.
- **Workflow-consumed artifacts:** generated files that repository workflows already depend on, or outputs the user explicitly asks to standardize.
- **Disposable run artifacts:** ad hoc debug scripts, copied reports, temporary screenshots, traces, videos, downloads, storage state, JSON/HTML dumps, and investigation notes serving only the current run.

## Placement Rules

1. Put requested deliverables where their peers already live — the maintained knowledge-base/project path a reader would look for them. If there is no clear peer or path, ask the user where it belongs instead of defaulting to a temporary/scratchpad directory. Never treat a requested deliverable as disposable, and do not delete it on completion. A session-level "put temporary files in the scratchpad" instruction does not override this — it governs disposable run artifacts, not a deliverable the user asked you to produce; when the two seem to conflict, the deliverable's placement wins.
2. Put project assets in the maintained project path.
3. Put workflow-consumed artifacts in the project's existing gitignored output path.
4. Put disposable artifacts in `mktemp -d`, `$TMPDIR`, or `/tmp` unless a working-tree path is required.
5. When you cannot immediately tell whether an artifact is disposable or worth keeping, apply the reuse test: would a future run, a teammate, or a fresh machine need it again (a config, an automation/bootstrap script, a reusable fixture)? If yes it is a project asset (rule 2); if it only serves the current run it is disposable (rule 4). If it is still genuinely ambiguous, ask the user; if you cannot ask (a non-interactive or CI run), fall back to treating it as disposable rather than writing it into the working tree.
6. Delete temporary project-local artifacts before completion unless the user asks to keep them.

## Playwright Defaults

- Treat test specs, page objects, shared fixtures, helper utilities, stable config changes, and intentional snapshots as project assets.
- Treat `playwright-report/`, `test-results/`, `blob-report/`, and JUnit/JSON outputs as workflow-consumed only when project workflows use them.
- Treat one-off traces, videos, screenshots, downloads, copied reports, temporary auth state, and ad hoc HAR/JSON/storage dumps as disposable.

## Hard Boundaries

- Do not create or widen `.gitignore`, config conventions, or repository directories just to host disposable outputs.
- Do not invent a project-local output convention unless the user explicitly asks for a reusable convention.
- Never place disposable artifacts in tracked or likely-to-be-committed paths such as repo root, `docs/`, `scripts/`, `tests/fixtures/`, or ad hoc folders.
- When a file is already under version control (git etc.), do not create `.bak`, backup, or timestamped duplicate copies of it before editing — history already preserves the prior state, so such copies are disposable clutter. Without version control, a pre-edit backup can be legitimate. If a *feature* needs to snapshot data (e.g. a pre-upgrade config backup), make it opt-in and default-off rather than always producing copies.
