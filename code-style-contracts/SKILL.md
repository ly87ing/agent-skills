---
name: code-style-contracts
description: Apply disciplined code style, config, data contract, naming, validation, and comment guidance. Use when writing or changing code, config files, schemas, serialized data, public contract fields, comments, or formatter/lint-sensitive files.
---

# Code Style Contracts

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
4. Keep comments rare and useful.
   - Explain invariants, edge cases, or tradeoffs.
   - Do not narrate obvious line-by-line behavior.
5. Re-read the diff before completion.
   - Remove accidental churn, dead code, debug leftovers, misleading names, and stale comments.
   - Before deleting code, confirm why it exists (check version-control history) and that it is truly dead.

## Stop Conditions

- A style change would reformat unrelated files.
- A data contract change lacks a compatibility or migration story.
- A comment explains intent that should instead be expressed by clearer code.
