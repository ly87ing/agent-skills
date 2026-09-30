---
name: reader-facing-writing
description: Write or revise reader-facing documents, plans, reports, proposals, specs, checklists, Markdown, HTML decks, dashboards, decision briefs, and agent-facing instruction files (AGENTS.md, CLAUDE.md) — and decide what each page or slide says and in what form, whether that is prose, a diagram, a screenshot, a before/after comparison, or a long screen recording trimmed and sped up into demo material an audience can actually follow. Use when content is meant for humans or agents to read, decide from, act on, review, or reuse, including compacting source material without losing its framework, when a broad rewrite is asked for with no target tone, structure, or ordering given and the target has to be agreed before executing, when a change has to land across mirrored artifacts such as a script and its rendered deck, and when turning raw captures into material that carries a point to an audience. A one-pager or dashboard counts when its job is to carry a conclusion to a named audience, charts included.
---

# Reader-facing Writing

A reader-facing artifact has one job, a page budget, and a figure wherever the content has a shape. First drafts run two to three times too long because they answer every question instead of the reader's; the skeletons below set the size, and the closing pass deletes down to it.

## Workflow

1. Fix the reader and the job. Decide who reads, what they already know, and whether they must decide, do, look up, or understand. One artifact, one job; a second job becomes a note or a linked artifact. Do not label the audience, purpose, or writing process in the artifact: no "for the on-call lead" in a title, no background section about the document itself (context about the system is content and stays); the opening starts with what the reader came for. Preserve a structure, framework, or correction list the user supplied, and treat requested prominence as a delivery contract, not a footnote. For a large subjective rewrite with no target tone, structure, or ordering, show a compact outline or 2-3 options before executing.
2. Pick the skeleton and its budget from the table below. The budget is a ceiling for the main path; everything the main path does not need goes to one named detail layer (appendix, linked page, click-to-open), never to a second overview.
3. When the output is HTML (a page or a fragment of one) or a deck, or carries a chart, diagram, screenshot, before/after pair, recording, or GIF, first read [references/visuals-and-decks.md](references/visuals-and-decks.md). Draft each section as one screen. Head it by the reader's job: a claim where they decide or understand, an action or outcome where they do (a how-to's numbered steps), a searchable term where they look something up. Under it, the figure or table that carries the relationship when the content has a shape (the skeleton's default figure), at most five sentences that argue from it, and a link to detail. Choose the figure with the form table, and its rendering by the target medium: Markdown on a code host renders static images, Mermaid, and GIF; an HTML page or deck can also carry video, step-by-step reveal, and click-to-open evidence, with a static fallback for each.
4. Preserve source truth. Keep the source framework when condensing; use source wording for numbers, names, owners, and dates; keep observation, self-report, inference, and unknowns distinct, and mark unknowns TBD or cut them (a TBD is resolved or removed before a view-only audience sees it). When shipped and planned items share a list, tag maturity inline. Keep the scope that qualifies a claim (environment, period, population, excluded cases) beside it, and keep it there when the claim is compressed into a table: "79 nodes" measured on a sampled development cluster, placed unqualified in a delivery-shape matrix, read as the product's delivery size and had to be re-labelled as sample data. Never assert a capability or track record of your own side you only inferred, and never fill a length quota with invented detail. Read [references/shaping-checklist.md](references/shaping-checklist.md) when sources conflict, mix delivered with planned, or were written for a different audience, and when a reader says the structure or focus is unclear.
5. Before drafting sentences, read [references/prose-style.md](references/prose-style.md) and apply it: active voice, one idea per sentence, no announcements, no meta-commentary, terms calibrated to the reader.
6. Once a full draft exists, and again after any feedback on the whole artifact rather than one spot, read [references/revision-pass.md](references/revision-pass.md) and run it to delete to budget: drop every sentence whose removal loses no fact and every visual whose removal makes no relationship harder to see, then run the entry-point, findability, and doing-path tests and the reader counts (`scripts/reader_check.py` counts), reporting each result when you deliver. The delete pass never removes prerequisites, commands, decision points, rollback, or done checks from a how-to, and leaves bold only on the few decisions, dates, or numbers a skimmer must catch. Report what stays unverified; an author reread never proves a human understood it.

## Skeletons and budgets

Pick by the reader's job. Sections are in order; a section the material cannot fill is dropped, not padded. One page means about 400-500 words of Markdown or one screen without scrolling.

| Artifact | Skeleton (in order) | Main-path ceiling | Default figure |
| --- | --- | --- | --- |
| Decision brief | Recommendation and why now; options on the same fields; what is asked of the reader | 1 page | Comparison table |
| Incident review | Impact in one line; root cause and contributing factors; what was done; what remains, with owner and date; timeline in the detail layer | 1 page | Timeline table |
| Design doc / RFC | Context and scope; for a replacement, each problem's cause in the current design and what the new one removes; goals and non-goals; design; alternatives and their trade-offs; cross-cutting concerns; rollout; open questions | 3 pages; 1 page for an incremental change | Context diagram when the change touches more than one component; a sequence diagram per flow that crosses a boundary; old beside new for a replacement |
| How-to / runbook | Trigger; prerequisites; numbered steps, each with its check; stop, rollback, and whom to escalate to; done criterion | 12 steps; split beyond that | Screenshot of the decisive state, or a state diagram |
| Action plan / checklist | One item per line: verb-first action, single owner, absolute date or concrete phase, done criterion; items parallel and in one order (time, structure, or importance); open items marked TBD, never invented | One screen | Table |
| Status report | Takeaway; blockers and risks; each number with what it counts and its basis; what changes for the reader; next actions with owner and date | 1 page | None; a table when several metrics recur, sorted bars only for a ranking |
| Multi-topic brief or meeting pre-read | Agenda naming each topic; one section per topic; next actions per responsible role | 1 screen per topic | One figure per topic where the topic has a shape |
| README | What it is in one line; quick start that works as pasted; one minimal example; links to the deeper docs | 1 screen before the first link | Screenshot or GIF of the result, only when the result is visual |
| Release notes | What changed for the user, grouped by impact, breaking changes and required upgrade actions first; internal refactors omitted | 1 line per change | None |
| Meeting notes | Decisions made; actions with owner and date; open questions; no transcript | 1 screen | Table |
| Change handoff note (for QA, ops, or the next owner) | What changed, deletions included, one line each, named by the behaviour and not by merge request, class, or review round; what the user can perceive; how it is designed, so a tester can derive cases; what to test, in priority order; what is not a defect; what must be prepared; what the developer has verified; who still has to confirm what; what to watch at rollout; developer contact | 1 page; details as a linked appendix | Table of changes; a diagram only for a flow the tester cannot infer |
| Notice | The change, who is affected and who is not, when | One paragraph | None |
| Reference / lookup, API reference | Searchable headings; signature or field, parameter table, one example, errors; no narrative | No prose beyond a lead line | Table |
| Agent instruction file (AGENTS.md, CLAUDE.md, a rules doc) | Commands, paths, boundaries (what may and may not change), and hard rules stated as their executable part; no mission, ownership, vision, process asides, or slogans; titled with the repository name | Every line whose removal would not change what the agent does is deleted | None |

A deck follows the same skeleton as its subject, one claim per slide as the headline with the proving visual beneath it; a new audience gets one slide on what the subject is before any implication.

## Form by content shape

The figure exists to make the content easier to understand, so the content decides. If one plain sentence carries the point, the sentence wins and no figure is added; a figure that restates a sentence is the same redundancy in a second medium. Default to a figure when the content is a structure, a flow, a sequence, a hierarchy, a comparison on the same fields, or change over time, because those shapes cost the reader more to rebuild from prose than to read from a picture. Keep to a sentence when the content is one conclusion or one or two numbers, and to a table when the reader will look values up.

| Information the reader needs | Form |
| --- | --- |
| One conclusion or a few facts | A sentence or a single large figure |
| Exact values or repeated fields across items | A table |
| Several options compared on the same fields | An aligned comparison table |
| Ranking on one measure | Bars sorted by value, labelled directly |
| Named events or milestones over time | A timeline |
| Numeric change over time | A line chart |
| Interaction over time between parties | A sequence diagram |
| Branched process, decision path, proven causal chain | A flowchart |
| Parent-child structure | A tree, never a mind map |
| Part of a whole | A stacked bar |
| Distribution of many values | A histogram |
| Components and their boundaries | A context or architecture diagram |
| Proof that something occurred | The real screenshot, record, or result |

- Title every figure with its takeaway and state its basis. Under it, write only what the figure cannot carry: the conclusion, the mechanism behind one arrow, or a caveat. A sentence that retells the arrows, rows, or steps in order is deleted, even when it feels like a courtesy to the reader.
- An arrow, a step number, or an operator is a factual claim of sequence, causation, or arithmetic. Connect only items whose data proves that relationship; keep independent metrics separate and labelled as not comparable.
- Draw the diagram in the form its medium renders best: Mermaid or the project's diagram format in Markdown on a code host, where the source lives beside the content; authored SVG or HTML geometry in an HTML page; native shapes in a deck. A Mermaid render pasted into an HTML page or a slide is auto-layout quality in a medium that can carry authored geometry. Keep one diagram to one question at one altitude and at most 15 nodes; split rather than crowd. Companion skills, when available, own the rest: `verification` browser and rendered-surface acceptance; `artifact-hygiene` placement, redaction, packaging, and handoff. This skill owns the visual's need, question, and takeaway. If a companion is unavailable, use only the fallback in `visuals-and-decks.md` and report what stays unverified.
- Two or three counts with no series, distribution, or comparison stay as a sentence or as large directly labelled figures with their basis, even when the request asks to make them visual; a proportion bar or card layout for two numbers is a chart the data has not earned, and building it as HTML is the same chart at a higher cost.
- A numbered procedure is already a sequence: do not add a flowchart that restates its steps. Give a how-to a figure only for a branch the steps cannot show in order, or a screenshot of the state the operator must recognize.

## Examples

**Incident review.** The source: search returned timeouts from 14:02 to 14:31; a cache TTL had been deployed as 0 instead of 300; rolling back the config restored service; the permanent fix is merged but not released; Owner B releases it on September 3.

Before, scaffolding around 40 words of fact:

> This document is intended for the on-call lead and summarizes the incident that occurred this afternoon. Background: at 14:02 the search service began returning timeouts. The team investigated and, after a period of analysis, identified that the cache configuration was incorrect. A rollback was performed at 14:31, after which service was restored. Root cause analysis showed the TTL was 0 instead of 300. Next steps: the permanent fix has been merged and will be released. Summary: the incident lasted 29 minutes and the root cause has been identified and will be addressed.

After:

> **Search returned timeouts for 29 minutes (14:02-14:31); the permanent fix is merged but not released.**
>
> Root cause: cache TTL deployed as 0 instead of 300. Rolling back the config restored service.
>
> | Item | Owner | Date |
> | --- | --- | --- |
> | Release the TTL fix | Owner B | Sep 3 |

**Call chain for reviewers.** The source describes an upload service that calls a scan service synchronously, scan calls a metadata service, and metadata writes to a queue; when scan is slow, each upload worker stays blocked, and the worker pool empties.

Before: the four hops and the failure written as one paragraph, which every reviewer reads twice.

After: a sequence diagram with a one-line takeaway and the one sentence the diagram cannot carry.

> **A slow scan blocks an upload worker for the whole call, so a scan slowdown empties the worker pool.**
>
> ```mermaid
> sequenceDiagram
>   Client->>Upload: file
>   Upload->>Scan: scan (sync, worker blocked)
>   Scan->>Metadata: lookup
>   Metadata->>Queue: enqueue
>   Scan-->>Upload: result (slow)
>   Note over Upload: worker held until Scan returns
> ```
>
> Scan's latency is inherited by every caller because the upload-to-scan call is synchronous; making that call asynchronous is the change under review.

**Replacement proposal, opening.** The source: the config center stores and ships every service's whole config file, re-renders each file a changed value touches, and patches files by text replacement.

Before: a problem-approach-cost paragraph and a 30-row component table; the principle came three sections later.

After, first screen:

> **The config center should hold only values; today it also stores, re-renders, and patches service files.**
>
> | Job it does today | What goes wrong | Handed to |
> | --- | --- | --- |
> | Stores and ships whole files | No proof which instance runs which file | The service image |
> | Re-renders files when a value changes | Saving one database configuration: 70.6 s | The service, reading values at startup |
> | Patches files by text replacement | About 210 rules fail silently | The framework, reading by key; a missing key fails startup |
>
> One practice causes all three, so tuning cannot remove them; handing the jobs back does.

**Change handoff note.** A change that removed an upload endpoint, added a rate limit on third-party downloads, and moved files to a new path went through three descriptions. Version one listed merge-request numbers, class names, and four review rounds; the tester could not find what to test, and none of those identifiers survive into the note. Version two was rewritten for the tester and lost the list of what changed. Version three:

> | Change | Kind | Visible to users |
> | --- | --- | --- |
> | `/upload/legacy` removed | Deletion | Old clients get 404; new path unchanged |
> | Third-party downloads rate-limited (20/min per tenant) | Behaviour | Bursts above the limit wait, not fail |
> | Files served from `/appdownload/` alongside the old path | Path | Both URLs work until the next release |
>
> Design: the service probes the target before uploading and reuses an existing identical file, so a retry of a published file never truncates it. Test first: upload the same package twice and interrupt one; then a burst of 30 downloads; then the old URL. Not a defect: the old URL still serving for one release.

**Notice.** Two numbers and a date do not need a title, a background section, or next steps:

> Old login closes Friday 18:00. Signed-in users are unaffected. Anyone not moved to the new login by then cannot sign in on Monday.
