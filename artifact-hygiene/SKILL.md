---
name: artifact-hygiene
description: Decide safe locations and cleanup rules for generated files, debug output, Playwright traces/screenshots/videos, downloaded artifacts, temporary scripts, reports, storage state, JSON/HTML dumps, and workflow-consumed outputs. Use before creating or keeping artifacts that might pollute a repository or be accidentally committed.
---

# Artifact Hygiene

## Classify Outputs

- **Project assets:** maintained source code, shared helpers, stable fixtures, maintained config, approved snapshots, and durable docs.
- **Workflow-consumed artifacts:** generated files that repository workflows already depend on, or outputs the user explicitly asks to standardize.
- **Disposable run artifacts:** ad hoc debug scripts, copied reports, temporary screenshots, traces, videos, downloads, storage state, JSON/HTML dumps, and investigation notes serving only the current run.

## Placement Rules

1. Put project assets in the maintained project path.
2. Put workflow-consumed artifacts in the project's existing gitignored output path.
3. Put disposable artifacts in `mktemp -d`, `$TMPDIR`, or `/tmp` unless a working-tree path is required.
4. Treat uncertain artifacts as disposable.
5. Delete temporary project-local artifacts before completion unless the user asks to keep them.

## Playwright Defaults

- Treat test specs, page objects, shared fixtures, helper utilities, stable config changes, and intentional snapshots as project assets.
- Treat `playwright-report/`, `test-results/`, `blob-report/`, and JUnit/JSON outputs as workflow-consumed only when project workflows use them.
- Treat one-off traces, videos, screenshots, downloads, copied reports, temporary auth state, and ad hoc HAR/JSON/storage dumps as disposable.

## Hard Boundaries

- Do not create or widen `.gitignore`, config conventions, or repository directories just to host disposable outputs.
- Do not invent a project-local output convention unless the user explicitly asks for a reusable convention.
- Never place disposable artifacts in tracked or likely-to-be-committed paths such as repo root, `docs/`, `scripts/`, `tests/fixtures/`, or ad hoc folders.
