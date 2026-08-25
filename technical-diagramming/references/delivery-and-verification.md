# Delivery And Verification

Use this reference for rendered SVG/HTML, comparison artifacts, or handoff.

## Source And Artifact Contract

- Keep one editable source of truth. If a renderer produces SVG or HTML, record the
  exact source file and command or maintained build entry point that produced it.
- Freeze the source before final rendering. Write the render to a private
  same-directory candidate, run the checks against that candidate, and atomically
  replace the accepted artifact only after all required checks pass. A failure leaves
  the previous accepted artifact untouched.
- When source and artifact are separate files, compute SHA-256 and byte counts for
  both after acceptance. A receipt proves byte identity and completed checks, not
  factual correctness or visual quality.
- Keep runtime dependencies self-contained for an offline handoff unless the user
  explicitly chooses a network-dependent artifact. Escape authored strings and never
  add telemetry, remote scripts, or active links that disclose repository or internal
  topology without the audience and destination permitting them.

## Semantic Checks

- Parse the editable source with its real parser or renderer.
- For SVG, run `scripts/validate_svg.py <candidate.svg>`. By default it rejects
  non-local dependencies so an offline artifact cannot silently load machine-local or
  network resources. Use `--allow-external` only when the user explicitly selected a
  network-dependent artifact, and report that choice in `unverified`. Exit 0 prints an
  `OK` summary; exit 1 lists diagnostics and fails the semantic gate.
- Reject duplicate IDs, missing endpoints, invalid references, impossible state
  transitions, and source links that do not exist at the stated revision.
- Confirm every visual boundary, arrow direction, label, style, and comparison status
  matches the authored semantic fact.
- For comparisons, verify both sides use the same scope and that layout-only movement
  is not reported as a system change.

## Render Checks

- Open the exact accepted artifact, not an earlier preview or cached render.
- Check console errors, missing resources, broken interactions, keyboard and focus
  behavior when interactive, text at 200% zoom, contrast, and page-level horizontal
  overflow at a narrow viewport.
- Check every intended desktop or presentation viewport for clipping, overlaps,
  unreadable labels, ambiguous edge corridors, broken legends, and excessive empty
  space that hides the primary path.
- Check light and dark themes when both are offered. Wait for fonts, images, and motion
  to settle before capturing evidence. A screenshot covers one state at one size, not
  the whole interaction.
- Read the render as the target reader: what the eye reaches first, whether the main
  question can be answered, and whether any line, color, position, or animation claims
  a relationship the evidence does not support.

## Receipt

Report only fields that exist for the chosen format:

```text
diagram_type: architecture|workflow|sequence|dataflow|lifecycle|comparison
source: <absolute path>
artifact: <absolute path or not generated>
evidence_basis: <revision, environment, or user-supplied description>
source_sha256: <hash or not applicable>
artifact_sha256: <hash or not applicable>
semantic_checks: passed|failed with diagnostics
render_checks: passed|failed|skipped with reason
visual_review: passed|failed|not performed
unverified: <bounded list>
```

Do not use `passed` for a check that did not execute. Do not claim visual review from
DOM inspection, command output, or automated screenshots without reading the rendered
pixels. A diagram of declared architecture does not prove the matching services are
deployed, healthy, reachable, or receiving traffic.
