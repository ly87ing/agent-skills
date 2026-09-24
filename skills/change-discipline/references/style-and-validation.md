# Style, naming, validation, comments

Read this when the change has a style, naming, input-validation, or comment dimension
— including serialized config where a value can change how the file parses, a formatter
run, or deleting a test or guard.

1. Match the local style first.
   - Use the repository's established formatter, lint, type-check, naming, and file layout.
   - New warnings introduced by your change count as regressions.
   - Stop if a style change would reformat unrelated files: keep the diff to what the change itself needs, and land a broad reformat as its own commit.
   - Run a formatter only on the files you changed, and before staging, diff for pure-format churn (re-indentation, wrapping) in lines you did not otherwise touch and revert it. Case: a repository-wide `cargo fmt` reformatted two files that carried the user's own uncommitted edits, and a re-indentation of one component produced a hundred lines of diff with no semantic change.
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
   - Stop if the comment explains intent that clearer code should carry instead — rename or restructure rather than annotate.
5. Re-read the diff before completion.
   - Remove accidental churn, dead code, debug leftovers, misleading names, and stale comments.
   - When told a resource is retired, handle its sibling retired resources in the same change rather than leaving them half-removed; the literal-string sweep for each is the hard gate's.
   - Distinguish a tombstone guard (a test asserting a removed feature stays gone — safe to delete along with the feature) from a build-safety/security guard (content or invariant checks kept for a build or security reason). The commit that added the guard tells you which; do not delete the latter as "redundant".
