# Style, naming, validation, comments

Read this when the change has a style, naming, input-validation, or comment dimension
— including serialized config where a value can change how the file parses, and any
final diff re-read before declaring the change done.

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
