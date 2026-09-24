# Shaping checklist

Read this when the artifact is larger than a notice, when the source material is
contested or mixed, or when a reviewer flags a structural problem. `SKILL.md` carries
the defaults — reader and job, skeletons, source truth, headings, emphasis, action
items — and this file carries only the long-tail rules behind them. None of them
license adding scaffolding: every rule here decides what a line says, not whether the
artifact needs another section.

## Reader fit

- Fit the main path to the reading occasion: minutes of linear reading for a brief, one direct hit for a lookup, an executable path for an operator. For several occasions, optimize for the most frequent and demote the rest.
- Required formal metadata (an RFC header, a document-control block) stays where its convention expects it; the rule against labelling the audience governs the visible opening, not that block.
- A second job first becomes a note; it becomes a separate linked artifact only when that layer can stand alone.
- Scope content to what the reader owns and must act on; name a boundary around mechanics owned by another layer instead of exposing internals the reader cannot change.
- Calibrate the opening to familiarity. Lead a familiar audience with what the material means for them; for a new audience first establish what the subject is, then its implications.
- In a persuasive brief to domain experts, state facts, capabilities, and evidence without instructing them how to do work they own. A doing or teaching artifact instructs its operator directly. Address a mixed audience as one room, and state the case on its own terms rather than against a named competitor.
- When a structure or prominence the user supplied conflicts with the artifact's job, propose the change instead of silently overriding it.
- Match scope and length to verifiable material: research accessible public gaps, ask only for user-owned facts, or narrow the deliverable.

## Source truth

- Never turn a screenshot, result, or second-hand account into an action or firsthand experience the source did not establish.
- Default to the conservative reading of your own side's record: an internal pilot is not a product, one good result is not a routine one, and a practice with no recorded start is not "for years".
- State each claim at the scope its evidence supports, and avoid universal quantifiers ("all", "everyone", "never") unless literally true.
- When reporting an improvement, give the local gain and the end-to-end gain it actually produces, and explain why they differ.
- Preserving source truth is not adopting the source's framing: when the source was written for a different audience or organization, keep its verified facts but re-fit its stance, scope, and examples to what is true for your reader.
- A number supports a claim only if it measures that claim over a matching period and population — a baseline gathered before the change you are crediting cannot show that change's effect. Cut such data or reframe the claim, and never add figures to look rigorous.
- When two sources disagree (a registry and a synced overview, a ticket and a chat summary), recompute from the primary record, treat the secondary as a claim, and mark what neither source can establish as unverified.
- Never present future or aspirational state as current.

## Reading path

- Treat the first screen as the reader's entry point, not a template. For deciding or understanding, it exposes the conclusion, why it matters now, and only the context needed to interpret it; for doing, the trigger or prerequisite and first action; for lookup, the search terms or map. A reader who stops there still knows the point and where detail lives.
- Establish hierarchy through position, size, proximity, alignment, and whitespace before decoration. Keep peer items visually parallel, with the same fields in the same order, sequenced on one logic — time, structure, or importance.
- Lead each section and paragraph with its takeaway; front-load the words that distinguish one part from the next.
- Break a screen-long wall at its idea boundaries into short paragraphs, a list, a table, or a figure. Keep table cells to values the reader compares; a cell that grows into a paragraph belongs in prose or the detail layer.
- Structural emphasis and emphasis the user supplied sit outside the bold budget. When most elements are emphasized, none rank.
- Layer a document set the same way: one overview carries the shared conclusion and maps each file to the question it answers; each member opens with its own takeaway and place in that map.
- Aggregate raw counts into the categories that carry the insight, or cut numbers that do not.
- Give an unfamiliar named entity a plain one-line identity on first appearance and the evidence that makes it relevant when it supports a judgment. Do not redefine tools the audience already uses.
- State the artifact's organizing logic in one sentence and place every section by it. Each section's body answers the question its heading raises. Announced counts match the body one-to-one; parts are non-overlapping and collectively complete; each fact or caveat lives in one place with named cross-references.

The entry-point, findability, and doing-path tests, and the two-part answer when asked whether comprehension was proved, are in [revision-pass.md](revision-pass.md).
