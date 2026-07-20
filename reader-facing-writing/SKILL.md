---
name: reader-facing-writing
description: Write or revise reader-facing documents, plans, reports, proposals, specs, checklists, Markdown, HTML decks, dashboards, decision briefs, and agent-facing instruction files (AGENTS.md, CLAUDE.md) — and decide what each page or slide says and in what form, whether that is prose, a diagram, a screenshot, a before/after comparison, or a long screen recording trimmed and sped up into demo material an audience can actually follow. Use when content is meant for humans or agents to read, decide from, act on, review, or reuse, including compacting source material without losing its framework, when a broad rewrite is asked for with no target tone, structure, or ordering given and the target has to be agreed before executing, when a change has to land across mirrored artifacts such as a script and its rendered deck, and when turning raw captures into material that carries a point to an audience.
---

# Reader-facing Writing

## Workflow

1. Fix the reader and decision.
   - State scope and the key takeaway up front.
   - Give just enough context and the trigger for why this matters now before the detail.
   - Match depth, terminology, and format to what the reader must decide or do.
   - Scope content to the reader's role: cover what they own and must act on, and abstract mechanics owned by another layer (for example platform-managed versus developer-owned configuration) behind a named boundary rather than exposing internals they cannot change.
   - Pitch detail to the document's purpose; when the goal is to change how people think or act, lead with what it means for the reader and cut detail below that purpose.
   - Calibrate the opening to the audience's starting familiarity: for an outward or introductory piece to readers new to the subject, first establish what the subject is in the plainest terms before its implications — a fresh audience cannot absorb what a thing means for them until they know what the thing is. Lead straight with implications only when the reader already knows the subject.
   - For a large restructure or subjective rewrite where the user has not specified the target tone, structure, or ordering, show a compact target outline or 2-3 concrete options before executing. For small edits or explicit user directions, proceed directly and preserve choices already made.
   - Do not instruct an audience on work they own: state your own facts, capabilities, and evidence, and let them draw the operational conclusions. Advice aimed into their expertise reads as condescension and discredits the material that would otherwise have persuaded them. For the same reason, address a mixed audience as one room — do not aim a section or a "now it's your turn" line at one segment, and state your position on its own terms rather than against a named competitor.
   - Treat a structure, framework, or list of corrections the user supplies as a standing checklist that survives every later revision: re-check each new draft against every item, and never let your own reframing quietly replace what they gave. If the given structure is wrong, say so and propose the change rather than drifting from it.
   - When the user asks for something at a given prominence — its own section, a demo, a page — a passing mention, a footnote, or a note to the presenter is not delivery. If it is genuinely redundant, say so and still produce it at the requested prominence unless the user agrees to drop it.
   - Meet a length or duration target by making fewer items land completely, not by adding items, trends, or figures — breadth added to fill a quota reads as padding to the very reader it was meant to impress.
2. Preserve source truth.
   - Keep the source framework when condensing; reword a layer, do not delete it.
   - Use source wording and figures for uncertain terms, numbers, names, owners, and dates.
   - Mark unknown values as TBD or cut them; do not invent to look complete. An internal uncertainty marker belongs in a working draft — before an artifact reaches an audience that will only view it, verify the value or remove the line.
   - Never assert a capability, maturity, or track record of your own side that you inferred from artifacts or plausibility — source every first-person claim from the user or a primary record, and default to the conservative reading: an internal pilot is not a product, one good result is not a routine one, and a practice with no recorded start is not "for years". These are the hardest claims for a reader to check and the most expensive to get wrong, because the room usually knows.
   - When one list, table, or section mixes what is delivered with what is planned, tag each item's maturity inline (shipped / in progress / proposed) — an aspiration sitting beside a shipped item is silently promoted to done by the company it keeps.
   - State each claim at the scope its evidence supports, and avoid universal quantifiers ("all", "everyone", "nobody", "never") unless they are literally true — a knowledgeable reader falsifies an absolute with one counterexample and discards the surrounding argument with it.
   - When reporting an improvement, give the local gain and the end-to-end gain it actually produces, and explain why they differ — a step-level speedup presented as the system-level outcome sets an expectation the system cannot meet.
   - Preserving source truth is not adopting the source's framing: when the source was written for a different audience or kind of organization, keep its verified facts but re-fit its stance, scope, and examples to what is true for your reader.
   - A number only supports a claim if it measures that claim over a matching period and population — a baseline gathered before the change you are crediting cannot show that change's effect. Cut such data or reframe the claim, and never add figures just to look rigorous.
3. Write for scanning.
   - Lead every section, paragraph, and item with its takeaway, and make that takeaway truly summarize what sits beneath it.
   - Keep peer items parallel, with the same fields in the same order, and sequence the items on one explicit logic — time, structure, or descending importance.
   - Prefer lists for long sentences and tables for dense or relational data; where order, hierarchy, or flow carries the meaning better than prose, reach for a diagram instead of describing it in words.
   - State what every figure counts and its basis (period, population, definition); a bare number or percentage the reader cannot interpret is noise — aggregate raw counts into the categories that carry the insight (which items are in scope and their status), or cut them.
   - Give every named entity — a tool, product, vendor, company, study, or internal codename — a plain one-line statement of what it is, plus one piece of evidence, the first time it appears. A bare name in a table is not information: the reader can tell neither what it is nor why it is there.
   - Be able to state the artifact's organizing logic in one sentence, and place every section by it — content supporting the same claim belongs together, and a section that cannot be placed by that logic is misplaced, not merely late. Pieces that each make sense alone still read as a collage when no single logic connects them.
   - When a section or agenda announces what follows ("three fronts", "two impacts"), make the enumeration match the body one-to-one in count, naming, and order, and re-check it after every restructure.
   - Put one fact in one place and cross-reference instead of repeating.
   - When you split a topic into parts, make them non-overlapping and collectively complete — flag any gap or leftover "other".
   - For a multi-topic brief, open with an agenda of what it covers, give each item its own section, and close with next steps per reader written as action items (with owner, date, and done criteria).
4. Keep the prose plain.
   - Use active voice, specific verbs, one idea per sentence, and no marketing filler.
   - Cut every line that serves the author rather than the reader: slogans, disclaimers and scope hedges ("this is not a commitment"), stance assertions ("we believe", "trust us"), boasts about your own restraint ("no hype here, just facts"), rally lines aimed at the audience, and your own housekeeping decisions (where a file lives, what is version-controlled). The discriminator: a boundary statement about the evidence itself ("this is a prototype", "a human still approves each step") is content; a statement about how you are talking is filler, however true it is.
   - On a medium with a separate notes channel — a deck's speaker notes, a doc's margin — keep your own reasoning, caliber hedges ("do not overstate this"), and presenter navigation ("next slide") in that channel, not on the audience-facing surface, which carries only what the reader takes away. Your analysis of the material is not part of the material; sweep such leaked meta-commentary as a class, not one line at a time.
   - On a persuasion or advocacy piece, do not pour cold water: a true but deflating point still belongs, but state it and reframe it as the next opportunity, and move the defensive detail to the notes as rebuttal ammunition — change the emphasis, never suppress the truth. This is the counterweight to cutting rally lines: you still remove cheerleading, but a necessary caveat must set correct expectations without reading as a splash of cold water.
   - Calibrate terms to the reader: define what they won't know, don't explain terms they already use, and use each term consistently. Establish a name before it carries weight as evidence — say in one clause what a company, institution, study, or technique is, or the claim it supports lands as a bare assertion however authoritative that name is to you. The opposite failure costs as much: when something reads as unclear to a domain audience, the fix is almost always an ambiguous figure's basis or an undefined internal codename, not the vocabulary — translating terms they use daily into plain speech reads as condescension.
   - Put the literal mechanism next to every analogy, never in place of it — if the reader can ask "but what actually happens, and why does that follow?" and the text has no answer, the analogy is concealing a gap instead of closing one.
   - For a senior or expert audience, write each claim as a plain declarative judgment; colloquial metaphors, punning compressions, and rallying slogans read as lightweight and get cut — most of all in titles, which are judged hardest.
   - Decompress claims instead of telegraphing them: shorthand that packs a claim, its evidence, and its point into one fragment forces the reader to rebuild the logic and loses even an expert audience — state each as a self-contained sentence that lands without prior context.
   - Keep each example or aside no heavier than the point it makes.
   - Choose examples that are current, meaningful to this audience, and consistent with the claim they support — drop stale tools, insider-only cases, and any example that undercuts its own point.
   - Do not narrate the document itself.
5. For plans and action items, include time and done criteria.
   - Give every action item a single owner, a concrete verb-first action, and a due date.
   - Use an absolute date when committed; otherwise use a concrete week or phase.
   - Never present future or aspirational state as current.
6. Revise before done.
   - Re-read as the target reader, reading it aloud to catch stiff or unnatural phrasing; for high-stakes material, run separate passes each from one named viewpoint — a fresh audience seeing it for the first time, the decision-maker, an adversarial expert — and let a claim survive only if it withstands that viewpoint's follow-up question.
   - Cut redundancy, verify facts, and confirm each section starts with its takeaway.
   - Check that every section, element, and number visibly connects to the document's purpose and to the part before it — one that ties to neither is misplaced or filler and should go.
   - When you change a value that recurs — a name, number, date, owner, or cross-reference — search the whole document for every occurrence and stale pointer (counts, "task N", "see above/below", section labels) before declaring done.
   - Treat a defect the reader flags as one sample of a class, not a single instance: sweep the whole artifact for that class, fix every occurrence in the same pass, and report how many you found. Fixing only the cited instance conscripts the reader as your reviewer, and they will notice.
   - When a revision deletes, softens, or renames something, sweep for everything that depended on it — later callbacks ("as we saw with X"), labels, badges, counts, and structural pointers — because removing an antecedent turns every dependent line into a non-sequitur that its own author can no longer see.
   - When a deliverable exists as mirrored artifacts — a script and its rendered deck, an outline and its output, a spec and its implementation — apply every content change to all of them in one pass and re-read the others before declaring done; a stale mirror actively misleads its next reader.
   - Cross-reference by name ("see the section on X"), never by position ("see page 12", "as in the previous part"), while the structure can still change — positional pointers go wrong silently on the next reorder.

## Designing And Verifying Visuals

- For material that will be presented or demonstrated rather than read alone, show before telling: replace prose that asserts a claim with the artifact that demonstrates it — a screenshot, a diagram, a recording, a real case — and never state a belief or conclusion as a bare line of text when an instance would let the reader reach it themselves. Prefer a capture of the real thing over a drawing of it.
- Keep captured evidence raw: a screenshot, ticket, or terminal capture persuades precisely because it is the real artifact, so crop and redact it but do not redraw it into a tidy explainer — a recreated or retyped version reads as fabricated and loses the conviction the original carried. If the evidence you need does not exist yet, mark it TBD; never mock up a fake to fill the gap.
- A before/after comparison supports its claim only when the panels differ in the thing claimed and nothing else: hold theme, crop, dimensions, and state constant and re-capture, rather than pairing whatever images you were handed — otherwise the difference reads as the incidental variable, and a skeptic dismisses a real gain as cosmetic. This is the visual twin of the rule that a number must measure the claim it is cited for.
- An arrow, a step number (01 to 02), or an operator between elements is itself a factual claim — that the items happen in sequence, that one causes the next, or that they combine arithmetically — and the audience reads the implied relationship as proven. Connect only items whose data establishes that relationship; keep independent metrics or evidence of different provenance visually separate and labelled as not comparable, rather than wiring them into one chain the numbers do not support.
- Check that a recording is legible at viewing size before making it the main visual. When it is a terminal, dense small text, or a long scroll, make a static or before/after capture the primary visual and demote the recording to optional supporting evidence — a recording the audience cannot read proves nothing, however real it is. Make a capture legible by re-rendering its source at higher zoom and re-capturing natively, never by upscaling a low-resolution crop — interpolation only blurs it further.
- Read "trim this recording" as make it usable, not make it shorter: cut dead waiting time, speed-ramp the exploratory stretch and drop back to real time for the payoff, and crop away tool chrome, cost meters, and status bars that carry nothing for the audience. Say what the recording still cannot do (no audio, unreadable at the back of a room) instead of shipping a shorter version of an unusable one, and confirm frame-by-frame that the footage actually shows the event its caption claims — a caption describing one incident over video of another is worse than no clip.
- Let sensitive content, not duration, decide a recording's cut points: scan extracted frames across the whole span for names and identifying data — not only near the boundary where trouble is expected — and cut clear of every occurrence. Trust frames over timestamps, since a UI renders streamed content earlier than the log or transcript says it completed.
- Make content legibility the bar; keep decorative styling secondary, and use color only when it encodes meaning (category, severity, diff), not as ornament.
- When color carries meaning, pair it with a label, shape, or pattern so it reads without color.
- Match the visual to its information density: never spend a large diagram on a few facts — pick the most compact form that stays legible.
- Match the diagram type to the content: sequence diagram for interaction over time, flowchart or node graph for process and causal chains, a tree for hierarchy — and reserve mind maps for exploratory overviews, not formal structure.
- Encode values by position or length before angle, area, or color; avoid pie, 3D, and dual-axis charts.
- Start bar and area baselines at zero, and keep visual magnitude proportional to the data.
- Title each visual with its takeaway, and label series directly instead of relying on a legend.
- Auto-layout diagrams (e.g. Mermaid) render differently per tool (label width, fonts, rendering mode), so long or CJK-heavy labels can clip — prefer a table for such labels, keep diagram labels short, and render once to confirm nothing is cut before embedding.

## HTML And Interactive Documents

- Use readable scalable type that stays usable at 200% zoom.
- Meet contrast minimums: 4.5:1 for body text, 3:1 for large text and chart elements.
- Keep content readable at a 320px width without horizontal scrolling.
- Decide online/offline dependencies before building.
- Surface click-triggered details where the reader is looking — and to hold both readability and authenticity, keep one restateable conclusion in large type on the surface and demote the full-detail real artifact (a screenshot, report, or recording) to a click-to-open evidence layer opened only when challenged.
- When material does not fit the time or space budget, attach it as an explicitly optional item the reader can open on demand instead of deleting it — label it with wording that permits use ("open it whenever") rather than discouraging it ("we won't cover this"), and give it a click target big enough to hit live.
- Use one canonical visual per flow.
- Verify the rendered result before declaring completion.
- When re-verifying a local file you just edited in a browser, hard-reload with the cache disabled; otherwise a stale cache shows the previous version.
- For a deck meant to be projected and talked through (not read alone), size it for a room: large type and a generous content area that fills the screen with minimal empty margins, and a navigation menu or anchored sections a presenter can jump between rather than only scrolling top-to-bottom. Design for the room's real full screen — the OS-level full screen the venue will use, at its aspect ratio (16:9), with no leftover margins; a browser window's inline "full screen" is not the venue's. When the venue or design is dark-themed, adapt every element to it and tone down glare-bright text; a page that dazzles in a dark room reads as unfinished.
- Use motion only to aid comprehension — a progressive reveal that paces a dense slide, or an animated build that walks through a process step by step — never as decoration; a static form that reads instantly beats motion that delays the point.

## Agent-facing instruction files

When the reader is an agent that will act on the file (AGENTS.md, CLAUDE.md, or a rules/domain doc), optimize for density and executable content, not narrative.

- Keep only what the agent acts on: commands, paths, boundaries (what may and may not change), and hard rules stated as their executable part.
- Cut identity, ownership, vision, org-process asides, and slogans — an agent does not act on "owner: X team" or "define once, applies to everyone".
- Apply a delete test to every line: if removing it would not change what the agent does, remove it.
- Title the file with the repository name, not a marketing phrase.
