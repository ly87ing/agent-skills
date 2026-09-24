---
name: technical-diagramming
description: "Create and verify architecture, workflow, sequence, data-flow, lifecycle, deployment, and topology-comparison diagrams. Use when authoring, comparing, or semantically validating the diagram itself; not for quantitative charts, browser-only UI checks, or broader document design."
---

# Technical Diagramming

Build the smallest diagram that lets a reader recover the intended technical
relationship without inventing topology, order, causality, runtime activity, or
impact. This skill owns the diagram model and diagram artifact, in any medium: the
test is how fast the reader gets the relationship, not which format carries it. It does not make a
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
   - Give each durable node and relationship a stable semantic ID, and record its
     evidence beside it in the source: a comment or data attribute naming the file and
     line at the revision, the runtime observation, or `user-specified`.
   - Keep confirmed facts, user-specified design, inference, and unknowns distinct.
     Unless the project has its own convention, draw confirmed and user-specified
     elements solid, draw inferred ones dashed with `(inferred)` in the label, and
     leave unknowns undrawn but listed in the adjacent note as `unknown: <what>`. Put
     the encoding in the legend whenever an inferred element appears. Omit unsupported
     detail instead of completing the picture by plausibility.
2. Choose the semantic model before the visual form.
   - Use `architecture` for components and boundaries, `deployment` for where they
     run (hosts, clusters, regions, environments, network zones, replicas), `workflow`
     for ordered work and decisions, `sequence` for interactions over time, `dataflow`
     for movement and transformation of data, and `lifecycle` for states and
     transitions.
   - Use a comparison only when both snapshots have the same scope and stable IDs.
     Report structural additions, removals, changes, moves, and reroutes without
     inferring impact, risk, or merge safety from appearance alone.
   - Keep one diagram to one question at one altitude and at most 15 nodes. When the
     answer needs more, draw an overview that links to detail diagrams or detail
     cards instead of shrinking labels to fit.
   - Read [references/modeling-and-layout.md](references/modeling-and-layout.md) for
     the selected model, the medium, and automatic versus authored geometry.
3. Choose the medium, then author an editable source of truth.
   - Pick the medium the reader gets the relationship from fastest where it will be
     read. Mermaid or the project's diagram format suits Markdown on a code host;
     SVG, or shapes drawn natively in the page with HTML/CSS or canvas, suits an HTML
     page; native shapes suit a slide; a short animation (GIF or video) suits change
     over time, such as a rollout phase by phase or a message exchange. Prefer the
     project's maintained format and renderer when one exists.
   - Use authored geometry rather than auto-layout when position, coexisting states,
     nested boundaries, or several edge classes carry meaning; a Mermaid render pasted
     into an HTML page or deck reads as auto-layout next to authored geometry.
   - Whatever the medium, keep an editable source that regenerates the artifact:
     diagram text, SVG or HTML, or the script or frame list behind an animation. An
     animation also ships a static frame or step list carrying the same facts, since
     it cannot be paused, searched, or read by a screen reader.
   - Make one primary reading path obvious. Attach exceptions and supporting detail
     to the nearest relevant element instead of turning every fact into another node
     or edge.
   - Keep semantic labels, protocols, direction, synchrony, and boundary crossings
     when they affect meaning. Repair layout before deleting meaningful labels.
   - Keep generated output downstream of its editable source. Never hand-edit a
     generated artifact after its source has been frozen.
4. Validate and deliver.
   - Read [references/delivery-and-verification.md](references/delivery-and-verification.md)
     before creating a standalone deliverable in any medium, a comparison, or a handoff. It
     owns diagram-specific source, semantic, and render checks. When available, use
     `verification` for browser, interaction, focus, zoom, contrast, overflow,
     and responsive acceptance; use `artifact-hygiene` for placement, redaction,
     dependency packaging, cleanup, and handoff. The reference carries only minimum
     fallbacks for runtimes where those companion skills are absent.
   - Validate the source model, then the rendered artifact. Use a same-directory
     candidate and replace the last accepted artifact only after required checks pass.
   - For SVG, standalone or inline in a page, run
     [scripts/validate_svg.py](scripts/validate_svg.py) against the candidate. It checks XML structure, the root and viewBox, duplicate IDs, broken
     `use`, `url()`, and ARIA ID references, and non-local resource dependencies. It
     counts `<a>` links, to a detail card in the page or to a source file, without
     failing them. It does not prove layout, link targets, or safety. Other media are
     checked with their own renderer, per the reference.
   - Inspect the real render at its intended viewing sizes, and every frame of an
     animation at its playback size. Automated checks can
     prove syntax, references, containment, and repeatability; only an actual visual
     read can claim that the diagram is legible and communicates the right hierarchy.
   - Preserve a receipt for separate source and artifact files: paths, hashes or
     exact revision, checks performed, visual-review status, and unverified boundaries.

## Completion

Return the editable source path, rendered artifact path when requested, diagram type, medium,
evidence basis, semantic and render checks, visual-review status, and any facts that
remain inferred or unverified. Do not report a failed command as acceptance, a
screenshot as proof of every interaction, or a structurally correct diagram as proof
that the depicted runtime is deployed and healthy.
