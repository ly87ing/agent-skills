---
name: reader-facing-writing
description: Write or revise reader-facing documents, plans, reports, proposals, specs, checklists, Markdown, HTML decks, dashboards, and decision briefs. Use when content is meant for humans to read, decide from, review, or reuse, including compacting source material without losing its framework.
---

# Reader-facing Writing

## Workflow

1. Fix the reader and decision.
   - State scope and the key takeaway up front.
   - Give just enough context and the trigger for why this matters now before the detail.
   - Match depth, terminology, and format to what the reader must decide or do.
   - Pitch detail to the document's purpose; when the goal is to change how people think or act, lead with what it means for the reader and cut detail below that purpose.
   - For a large restructure or subjective rewrite where the user has not specified the target tone, structure, or ordering, show a compact target outline or 2-3 concrete options before executing. For small edits or explicit user directions, proceed directly and preserve choices already made.
2. Preserve source truth.
   - Keep the source framework when condensing; reword a layer, do not delete it.
   - Use source wording and figures for uncertain terms, numbers, names, owners, and dates.
   - Mark unknown values as TBD or cut them; do not invent to look complete.
3. Write for scanning.
   - Lead every section, paragraph, and item with its takeaway, and make that takeaway truly summarize what sits beneath it.
   - Keep peer items parallel, with the same fields in the same order, and sequence the items on one explicit logic — time, structure, or descending importance.
   - Prefer lists for long sentences and tables for dense or relational data; reserve diagrams for genuine process flows.
   - Put one fact in one place and cross-reference instead of repeating.
   - When you split a topic into parts, make them non-overlapping and collectively complete — flag any gap or leftover "other".
   - For a multi-topic brief, open with an agenda of what it covers, give each item its own section, and close with next steps per reader written as action items (with owner, date, and done criteria).
4. Keep the prose plain.
   - Use active voice, specific verbs, one idea per sentence, and no marketing filler.
   - Calibrate terms to the reader: define what they won't know, don't explain terms they already use, and use each term consistently.
   - Keep each example or aside no heavier than the point it makes.
   - Do not narrate the document itself.
5. For plans and action items, include time and done criteria.
   - Give every action item a single owner, a concrete verb-first action, and a due date.
   - Use an absolute date when committed; otherwise use a concrete week or phase.
   - Never present future or aspirational state as current.
6. Revise before done.
   - Re-read as the target reader, reading it aloud to catch stiff or unnatural phrasing.
   - Cut redundancy, verify facts, and confirm each section starts with its takeaway.
   - When you change a value that recurs — a name, number, date, owner, or cross-reference — search the whole document for every occurrence and stale pointer (counts, "task N", "see above/below", section labels) before declaring done.

## Designing And Verifying Visuals

- Make content legibility the bar; keep decorative styling secondary, and use color only when it encodes meaning (category, severity, diff), not as ornament.
- When color carries meaning, pair it with a label, shape, or pattern so it reads without color.
- Match the visual to its information density: never spend a large diagram on a few facts — pick the most compact form that stays legible.
- Encode values by position or length before angle, area, or color; avoid pie, 3D, and dual-axis charts.
- Start bar and area baselines at zero, and keep visual magnitude proportional to the data.
- Title each visual with its takeaway, and label series directly instead of relying on a legend.
- Auto-layout diagrams (e.g. Mermaid) render differently per tool (label width, fonts, rendering mode), so long or CJK-heavy labels can clip — prefer a table for such labels, keep diagram labels short, and render once to confirm nothing is cut before embedding.

## HTML And Interactive Documents

- Use readable scalable type that stays usable at 200% zoom.
- Meet contrast minimums: 4.5:1 for body text, 3:1 for large text and chart elements.
- Keep content readable at a 320px width without horizontal scrolling.
- Decide online/offline dependencies before building.
- Surface click-triggered details where the reader is looking.
- Use one canonical visual per flow.
- Verify the rendered result before declaring completion.
- When re-verifying a local file you just edited in a browser, hard-reload with the cache disabled; otherwise a stale cache shows the previous version.
