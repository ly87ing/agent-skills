---
name: reader-facing-writing
description: Write or revise reader-facing documents, plans, reports, proposals, specs, checklists, Markdown, HTML decks, dashboards, and decision briefs. Use when content is meant for humans to read, decide from, review, or reuse, including compacting source material without losing its framework.
---

# Reader-facing Writing

## Workflow

1. Fix the reader and decision.
   - State scope and the key point up front.
   - Match depth, terminology, and format to what the reader must decide or do.
   - Pitch detail to the document's purpose; when the goal is to change how people think or act, lead with what it means for the reader and cut detail below that purpose.
2. Preserve source truth.
   - Keep the source framework when condensing; reword a layer, do not delete it.
   - Use source wording and figures for uncertain terms, numbers, names, owners, and dates.
   - Mark unknown values as TBD or cut them; do not invent to look complete.
3. Write for scanning.
   - Lead every section, paragraph, and item with its takeaway.
   - Keep peer items parallel, with the same fields in the same order.
   - Prefer lists for long sentences and tables for dense or relational data; reserve diagrams for genuine process flows.
   - Put one fact in one place and cross-reference instead of repeating.
   - For a multi-topic brief, open with an agenda of what it covers, give each item its own section, and close with next steps addressed per reader — name the owner, and the deadline where it applies.
4. Keep the prose plain.
   - Use active voice, specific verbs, one idea per sentence, and no marketing filler.
   - Calibrate terms to the reader: define what they won't know, don't explain terms they already use, and use each term consistently.
   - Keep each example or aside no heavier than the point it makes.
   - Do not narrate the document itself.
5. For plans and action items, include time and done criteria.
   - Use an absolute date when committed; otherwise use a concrete week or phase.
   - Never present future or aspirational state as current.
6. Revise before done.
   - Re-read as the target reader, reading it aloud to catch stiff or unnatural phrasing.
   - Cut redundancy, verify facts, and confirm each section starts with its point.

## Sizing And Verifying Visuals

- Make content legibility the bar; keep decorative styling secondary, and use color only when it encodes meaning (category, severity, diff), not as ornament.
- Match the visual to its information density: never spend a large diagram on a few facts — pick the most compact form that stays legible.
- Auto-layout diagrams (e.g. Mermaid) render differently per tool (label width, fonts, rendering mode), so long or CJK-heavy labels can clip — prefer a table for such labels, keep diagram labels short, and render once to confirm nothing is cut before embedding.

## HTML And Interactive Documents

- Use readable scalable type, adequate contrast, and 200% zoom compatibility.
- Decide online/offline dependencies before building.
- Surface click-triggered details where the reader is looking.
- Use one canonical visual per flow.
- Verify the rendered result before declaring completion.
