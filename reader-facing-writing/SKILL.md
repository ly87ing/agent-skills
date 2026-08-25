---
name: reader-facing-writing
description: Write or revise reader-facing documents, plans, reports, proposals, specs, checklists, Markdown, HTML decks, dashboards, decision briefs, and agent-facing instruction files (AGENTS.md, CLAUDE.md) — and decide what each page or slide says and in what form, whether that is prose, a diagram, a screenshot, a before/after comparison, or a long screen recording trimmed and sped up into demo material an audience can actually follow. Use when content is meant for humans or agents to read, decide from, act on, review, or reuse, including compacting source material without losing its framework, when a broad rewrite is asked for with no target tone, structure, or ordering given and the target has to be agreed before executing, when a change has to land across mirrored artifacts such as a script and its rendered deck, and when turning raw captures into material that carries a point to an audience. A one-pager or dashboard counts when its job is to carry a conclusion to a named audience, charts included.
---

# Reader-facing Writing

## Workflow

1. Set the reader's task before drafting.
   - Before drafting, determine what the reader already knows, whether they need to decide, do, find, or understand something, what outcome the material should enable, and when or where they will read it.
   - Use those choices to govern depth, terminology, form, and omission. Do not automatically label the audience, purpose, or writing process in the artifact; the visible opening starts with what the reader came for, while required formal metadata stays where its convention expects it. Keep any scope that changes how a claim or its evidence must be interpreted — environment, period, population, definition, or excluded cases — visible beside that claim instead of hiding it as writing metadata.
   - Give each artifact one main job and split by job, not topic count. A decision brief that grows a reference inventory, or a how-to that grows design rationale, first demotes the second job to a note and becomes a separate linked artifact only when that layer can stand alone.
   - Fit the main path to the reading occasion: minutes of linear reading for a brief, one direct hit for a lookup, an executable path for an operator. For several occasions, optimize for the most frequent and demote the rest rather than stretching every reading path.
   - Scope content to what the reader owns and must act on; name a boundary around mechanics owned by another layer instead of exposing internals the reader cannot change.
   - Calibrate the opening to familiarity. Lead a familiar audience with what the material means for them; first establish what an unfamiliar subject is for a new audience, then explain its implications.
   - For a large subjective rewrite with no target tone, structure, or ordering, show a compact outline or 2-3 concrete options before executing. Proceed directly for small edits or explicit directions.
   - In a persuasive brief to domain experts, state facts, capabilities, and evidence without instructing them how to do work they own. A doing or teaching artifact should instruct its operator directly. Address a mixed audience as one room, and state the case on its own terms rather than against a named competitor.
   - Preserve a structure, framework, or correction list the user supplied across every revision. Treat requested prominence as a delivery contract: a section, page, or demo is not satisfied by a passing mention, footnote, or presenter note. If either choice conflicts with the artifact's job, propose the change instead of silently overriding it.
   - Match scope and length to verifiable material: research accessible public gaps, ask only for user-owned facts, or narrow the deliverable; never fill a quota with repetition, promoted inference, or invented examples.
2. Preserve source truth.
   - Keep the source framework when condensing; reword a layer, do not delete it.
   - Use source wording and figures for uncertain terms, numbers, names, owners, and dates.
   - Keep direct observation, source self-report, inference, and unknowns distinct; never turn a screenshot, result, or second-hand account into an action or firsthand experience the source did not establish.
   - Mark unknown values as TBD or cut them; do not invent to look complete. An internal uncertainty marker belongs in a working draft — before an artifact reaches an audience that will only view it, verify the value or remove the line.
   - Never assert a capability, maturity, or track record of your own side that you inferred from artifacts or plausibility — source every first-person claim from the user or a primary record, and default to the conservative reading: an internal pilot is not a product, one good result is not a routine one, and a practice with no recorded start is not "for years". These are the hardest claims for a reader to check and the most expensive to get wrong, because the room usually knows.
   - When one list, table, or section mixes what is delivered with what is planned, tag each item's maturity inline (shipped / in progress / proposed) — an aspiration sitting beside a shipped item is silently promoted to done by the company it keeps.
   - State each claim at the scope its evidence supports, and avoid universal quantifiers ("all", "everyone", "nobody", "never") unless they are literally true — a knowledgeable reader falsifies an absolute with one counterexample and discards the surrounding argument with it.
   - When reporting an improvement, give the local gain and the end-to-end gain it actually produces, and explain why they differ — a step-level speedup presented as the system-level outcome sets an expectation the system cannot meet.
   - Preserving source truth is not adopting the source's framing: when the source was written for a different audience or kind of organization, keep its verified facts but re-fit its stance, scope, and examples to what is true for your reader.
   - A number only supports a claim if it measures that claim over a matching period and population — a baseline gathered before the change you are crediting cannot show that change's effect. Cut such data or reframe the claim, and never add figures just to look rigorous.
3. Shape the information before writing prose.
   - Choose the lightest form that exposes the relationship the reader must perceive. Visual does not mean decorative image: position, grouping, alignment, whitespace, tables, and diagrams are all ways to make structure visible.

     | Information the reader needs | Default form |
     | --- | --- |
     | One conclusion or a few facts | A sentence or a compact figure |
     | Exact values or repeated fields across items | A table |
     | Several options compared on the same fields | An aligned comparison table |
     | Ranking on one measure | Bars sorted by value |
     | Named events or milestones over time | A timeline |
     | Numeric change over time | A line chart |
     | Interaction over time | A sequence diagram |
     | Branched process, decision path, or proven causal chain | A flowchart or node graph |
     | Parent-child structure | A tree |
     | Proof that something occurred | A real screenshot, record, or result |

   - A visual earns its place only when it reduces the work of reconstructing a relationship from prose. Do not spend a chart on one or two numbers, turn lookup data into a diagram, or add imagery merely because people scan visually.
   - A table or diagram replaces the prose for that relationship. Give it a takeaway and the context needed to interpret it; do not narrate every cell, node, or arrow again.
   - Arrows, sequence, spatial grouping, size, and color all assert relationships. Use them only when the source proves the implied sequence, causation, grouping, magnitude, or status.
   - When a technical diagram is warranted and `technical-diagramming` is available, keep the reader question, reason for the diagram, takeaway, and surrounding material here; let that skill own the technical model, geometry, diagram artifact, and diagram-specific semantic checks.
   - If the artifact contains or needs a chart, diagram, screenshot, before/after pair, recording, deck, dashboard, or HTML page, read [references/visuals-and-decks.md](references/visuals-and-decks.md) before choosing or designing it.
4. Build the visible reading path.
   - Keep structure proportional to content. A short answer or notice that one or two paragraphs can carry gets no automatic title, audience declaration, background section, agenda, summary, or next-steps wrapper.
   - Treat the first screen as the reader's entry point, not a template. For deciding or understanding, it exposes the conclusion, why it matters now, and only the context needed to interpret it; for doing, the trigger or prerequisite and first action; for lookup, the search terms or map. A reader who stops there should still know the point and where needed detail lives.
   - Demote, don't delete: cut what no reader needs, and move material only some readers need — inventories, per-case tables, raw evidence, or implementer detail — to one named detail layer that the main path cites with its one-line conclusion. Keep prerequisites, commands, decision points, rollback, and done checks in the main path of a how-to. Stop at the main path plus one cited detail layer so the reader does not dig through overviews of overviews.
   - Establish hierarchy through position, size, proximity, alignment, and whitespace before adding decoration. Keep peer items visually parallel, with the same fields in the same order, and sequence them on one logic — time, structure, or importance.
   - Match headings to the job: claim-led for deciding and understanding, action- or outcome-led for doing, and searchable terms for lookup. In briefs and reports, lead each section and paragraph with its takeaway; in every form, front-load the words that distinguish one part from the next.
   - Break a screen-long wall at its idea boundaries into short paragraphs, a list, a table, or an earned visual. Keep table cells to values the reader compares; a cell that grows into a paragraph belongs in prose or the detail layer.
   - Budget emphasis: bold or accent only the few decisions, deadlines, states, or numbers a skimmer must catch. Structural emphasis and emphasis the user deliberately supplied sit outside this budget; preserve them unless the user agrees to change them. When most elements are emphasized, none of them rank.
   - Layer a document set the same way: one overview carries the shared conclusion and maps each file to the question it answers; each member opens with its own takeaway and place in that map.
   - State what every figure counts and its basis (period, population, definition). Aggregate raw counts into categories that carry the insight, or cut numbers that do not.
   - Give an unfamiliar named entity a plain one-line identity on first appearance and the evidence that makes it relevant when it supports a judgment. Do not redefine tools the audience already knows.
   - State the artifact's organizing logic in one sentence and place every section by it. Each section's body answers the question its heading or takeaway raises. Make announced counts match the body one-to-one, keep parts non-overlapping and collectively complete, and put each fact or caveat in one place with named cross-references.
   - For a multi-topic brief, use the first screen as its map: name the topics, give each a matching section, and close with committed next actions per responsible role where the material supports them.
5. Keep the prose plain.
   - Read [references/prose-style.md](references/prose-style.md) and apply it while drafting sentences: it carries the wording rules — active voice, one idea per sentence, padding and Europeanized-Chinese patterns cut as classes, meta-commentary swept, terms calibrated to the reader. Short is a limit on wording, not on substance.
6. For committed plans and action items, include time and done criteria.
   - Give every committed action item a single owner, a concrete verb-first action, and a due date.
   - Use an absolute date when committed; otherwise use a concrete week or phase.
   - Keep exploratory options, open decisions, and unknown owners visibly separate; mark them TBD instead of inventing commitments.
   - Never present future or aspirational state as current.
7. Test comprehension before done.
   - Read [references/revision-pass.md](references/revision-pass.md) and run it once a full draft exists. Test whether the first view can be paraphrased correctly, key facts can be found, a doing artifact can be executed safely, and every visual makes a relationship easier to understand; then run the factual, delete-only, dependency, and mirrored-artifact sweeps. These author-side checks reduce likely failures but do not prove that a human reader understood the artifact; for high-stakes material, test with a representative reader when feasible or state that human comprehension was not validated.

## Rendered visuals and interactive artifacts

The reader question, need for the visual, takeaway, and surrounding content stay in this skill. When available, `technical-diagramming` owns a technical diagram's model, geometry, artifact, and semantic validation; `frontend-verification` owns browser and rendered-surface acceptance; and `artifact-hygiene` owns placement, redaction, dependency packaging, and handoff. If `technical-diagramming` is unavailable, use only the diagram fallback in [references/visuals-and-decks.md](references/visuals-and-decks.md). Do not absorb an unavailable companion's full workflow; report what remains unverified.

## Agent-facing instruction files

When the reader is an agent that will act on the file (AGENTS.md, CLAUDE.md, or a rules/domain doc), optimize for density and executable content, not narrative.

- Keep only what the agent acts on: commands, paths, boundaries (what may and may not change), and hard rules stated as their executable part.
- Cut identity, ownership, vision, org-process asides, and slogans — an agent does not act on "owner: X team" or "define once, applies to everyone".
- Apply a delete test to every line: if removing it would not change what the agent does, remove it.
- Title the file with the repository name, not a marketing phrase.
