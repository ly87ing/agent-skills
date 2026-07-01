---
name: code-style-contracts
description: Apply disciplined code style, config, data contract, naming, validation, and comment guidance. Use when writing or changing code, config files, schemas, serialized data, public contract fields, comments, or formatter/lint-sensitive files.
---

# Code Style Contracts

## Before you change anything that already exists (hard gate)

Applies to EVERY edit of existing code, a config/contract value, a test expectation, or any behavior — not only bug fixes. The mistake this prevents: treating a symptom (a failing test, a "wrong-looking" value/regex/field name, a reported defect) as the spec and flipping the code to match it, thereby re-introducing a bug a previous commit deliberately fixed.

- **Establish WHY the current state is what it is, before changing it.** Run `git log -S "<symbol/value>"`, `git log -L`, or `git blame` on the exact line/symbol you intend to change. Current behavior is often the deliberate result of an earlier `fix:[#…]` / `feat:`; the commit message + bug id tell you the intent. Two real near-misses: a removed dangerous-char `;` (its removal had fixed a log-download bug) and a removed mode-guard (its removal had restored automatic failover) — re-adding either to satisfy a stale test would have re-opened the bug.
- **A symptom is not a spec — decide DIRECTION from history + the real contract, not from the symptom.** Current behavior is a deliberate later decision → the test/expectation is **stale**: update it and record which commit/bug voided the old one. The test/contract is right and the code is incomplete (e.g. committed together yet contradicting) → change the code. Never flip a value or loosen a check just to make a symptom disappear.
- **Grep every caller/consumer of a shared symbol, signature, contract field, or config key before changing it, and run the neighboring tests.** A change that satisfies one site can break a real caller (e.g. a guard added for one test that blocks an automatic background path). Widening/loosening can't break existing-valid inputs but can have a security blast radius — check that too.
- **Verify the smallest thing that can actually fail, then prove no new regression.** Run the narrowest test that exercises the change and read the REAL result (`BUILD SUCCESSFUL` / `N failed`), never a piped command's `| tail` exit code. Before declaring done, confirm zero new failures (diff the failing set against a clean baseline). One fix often unmasks deeper drift — a unit is not done until its whole class/module is green.
- **If history shows the change sits on an unresolved design / security / contract decision, stop and escalate with the evidence instead of silently picking a side.** Leaving it unchanged-and-flagged is a valid outcome; quietly satisfying a symptom you lack the authority to interpret is not.

## Workflow

1. Match the local style first.
   - Use the repository's established formatter, lint, type-check, naming, and file layout.
   - New warnings introduced by your change count as regressions.
2. Use names with business meaning.
   - Avoid single-letter names and unclear abbreviations outside tiny local scopes.
   - Keep public fields and config keys consistent with existing contracts.
3. Validate inputs fail-close.
   - Reject malformed, unsupported, or ambiguous external input and config.
   - Do not silently coerce values unless an existing compatibility contract requires it.
   - In serialized config (YAML/TOML/JSON), keep values from changing the parse. An unquoted YAML scalar containing `: `, a leading `#`, or a `|`/`>` can silently reparse as a nested map, a comment, or a block scalar and load as the wrong thing — and a naive `split(":")` check won't catch it (a real case: an unquoted `description:` with `: ` in it made two skills silently fail to load). Quote the scalar, use ` — ` as an inline separator, and validate with a real parser, not string slicing.
4. Keep comments rare and useful.
   - Explain invariants, edge cases, or tradeoffs.
   - Do not narrate obvious line-by-line behavior.
5. Re-read the diff before completion.
   - Remove accidental churn, dead code, debug leftovers, misleading names, and stale comments.
   - Before deleting code, confirm why it exists (check version-control history) and that it is truly dead.
   - When told a resource is retired/no-longer-maintained, do a full-footprint sweep (`git grep` across code, tests, docs, Makefile, config, and wiring) and handle sibling retired resources together — do not clean up only the one that was named while leaving the rest half-removed.
   - Distinguish a tombstone guard (a test asserting a removed feature stays gone — safe to delete along with the feature) from a build-safety/security guard (content or invariant checks kept for a build or security reason). The commit that added the guard tells you which; do not delete the latter as "redundant".

## Stop Conditions

- A style change would reformat unrelated files.
- A data contract change lacks a compatibility or migration story.
- A comment explains intent that should instead be expressed by clearer code.
