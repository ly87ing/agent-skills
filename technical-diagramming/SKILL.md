---
name: technical-diagramming
description: "Create and verify architecture, workflow, sequence, data-flow, lifecycle, deployment, and topology-comparison diagrams. Use when authoring, comparing, or semantically validating the diagram itself; not for quantitative charts, browser-only UI checks, or broader document design."
---

# Technical Diagramming

Build the smallest diagram that lets a reader recover the intended technical
relationship without inventing topology, order, causality, runtime activity, or
impact. This skill owns the diagram model and diagram artifact. It does not make a
diagram necessary merely because a document could contain one, and it does not turn
the diagram into evidence stronger than its sources. When the diagram sits in broader
reader-facing material, accept the reader question, need, and surrounding argument from
`reader-facing-writing` when available rather than redesigning that material here.

## Workflow

1. Fix the question and evidence boundary.
   - State the one question the diagram must answer and whether its facts come from
     code, configuration, runtime observations, user-supplied design, or a mixture.
   - For repository-backed work, inspect the relevant entry points, callers,
     configuration chain, and exact revision before drawing. A directory name,
     README claim, or code search hit is a lead, not proof of a relationship.
   - Give each durable node and relationship a stable semantic ID. Keep confirmed
     facts, user-specified design, inference, and unknowns distinct; omit unsupported
     detail instead of completing the picture by plausibility.
2. Choose the semantic model before the visual form.
   - Use `architecture` for components and boundaries, `workflow` for ordered work
     and decisions, `sequence` for interactions over time, `dataflow` for movement
     and transformation of data, and `lifecycle` for states and transitions.
   - Use a comparison only when both snapshots have the same scope and stable IDs.
     Report structural additions, removals, changes, moves, and reroutes without
     inferring impact, risk, or merge safety from appearance alone.
   - Read [references/modeling-and-layout.md](references/modeling-and-layout.md) for
     the selected model and when choosing automatic or authored geometry.
3. Author an editable source of truth.
   - Prefer the project's existing diagram format and renderer when one is maintained.
     For a simple portable graph in Markdown that the host renders natively, Mermaid
     may be sufficient. Use explicit SVG/HTML geometry when position, coexisting
     states, nested boundaries, or several edge classes carry meaning that auto-layout
     cannot preserve, and for any HTML page or deck deliverable, where a pasted
     Mermaid render reads as auto-layout quality next to authored geometry.
   - Make one primary reading path obvious. Attach exceptions and supporting detail
     to the nearest relevant element instead of turning every fact into another node
     or edge.
   - Keep semantic labels, protocols, direction, synchrony, and boundary crossings
     when they affect meaning. Repair layout before deleting meaningful labels.
   - Keep generated output downstream of its editable source. Never hand-edit a
     generated artifact after its source has been frozen.
4. Validate and deliver.
   - Read [references/delivery-and-verification.md](references/delivery-and-verification.md)
     before creating a standalone HTML/SVG deliverable, a comparison, or a handoff. It
     owns diagram-specific source, semantic, and render checks. When available, use
     `frontend-verification` for browser, interaction, focus, zoom, contrast, overflow,
     and responsive acceptance; use `artifact-hygiene` for placement, redaction,
     dependency packaging, cleanup, and handoff. The reference carries only minimum
     fallbacks for runtimes where those companion skills are absent.
   - Validate the source model, then the rendered artifact. Use a same-directory
     candidate and replace the last accepted artifact only after required checks pass.
   - For SVG, run [scripts/validate_svg.py](scripts/validate_svg.py) against the
     candidate. It checks XML structure, the root and viewBox, duplicate IDs, broken
     URL/href/ARIA ID references, and non-local URL dependencies. It does not prove
     layout or safety.
   - Inspect the real render at its intended viewing sizes. Automated checks can
     prove syntax, references, containment, and repeatability; only an actual visual
     read can claim that the diagram is legible and communicates the right hierarchy.
   - Preserve a receipt for separate source and artifact files: paths, hashes or
     exact revision, checks performed, visual-review status, and unverified boundaries.

## Completion

Return the editable source path, rendered artifact path when requested, diagram type,
evidence basis, semantic and render checks, visual-review status, and any facts that
remain inferred or unverified. Do not report a failed command as acceptance, a
screenshot as proof of every interaction, or a structurally correct diagram as proof
that the depicted runtime is deployed and healthy.
