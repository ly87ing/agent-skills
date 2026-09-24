# Visuals, Decks, And HTML

Load this when the artifact carries a chart, diagram, screenshot, before/after pair, screen
recording, deck, dashboard, or HTML page. It holds the form-selection, evidence-integrity,
chart-encoding, projection, and accessibility rules those artifacts must pass; the prose rules
in `SKILL.md` still apply to every word on them.

Where the runtime ships a dedicated chart or visual-design skill, prefer it for the chart itself
and keep these rules for the page around it. Where none is installed, the chart is this skill's
job too rather than nobody's — a neighbour present on one runtime is not present on the next, and
deferring to one that was never loaded leaves the reader with an unowned visual.

The diagram rules below marked "in the fallback path" apply only when `technical-diagramming`
is unavailable; the split of ownership is in `SKILL.md`.

## Medium Capability

Choose the visual form the target medium can actually render, and give every moving form a
static fallback the reader can use when motion is blocked, printed, or unwanted.

| Medium | Renders | Does not render | Use motion for |
| --- | --- | --- | --- |
| Markdown on a code host (README, wiki, MR) | Static images, SVG, animated GIF, collapsible details, Mermaid where the host renders it; a host-uploaded video linked bare on its own line plays inline on GitHub and GitLab | HTML video tags and iframes (sanitized); elsewhere link a thumbnail to hosted video | A silent 2-4 step interaction that must play inline |
| HTML page or interactive document | All of the above, plus video with controls, step-by-step reveal, scroll-driven panels, click-to-open evidence, runnable examples | Nothing, but every layer adds page weight and a verification surface | A multi-step flow the reader paces themselves |
| Deck presented live | Static figures, per-slide builds, embedded video | Nothing the presenter cannot start and stop | Revealing one layer of a figure at a time |
| PDF, print, chat paste | Static only | Any motion | Nothing; ship the static frame |

- One state or one relationship is a static image or diagram, whatever the medium. Motion is for a process whose sequence is itself the content; do not animate to decorate a page that can carry motion.
- An inline GIF for a code host stays short and light: 5-15 seconds, 10-15 fps, 600-800 px wide, under about 5 MB, first and last frames matching so the loop does not jump. Record terminal demos from a scripted source (a tape or cast file kept in the repository) so the clip can be regenerated when the product changes.
- Narration, more than 15-20 seconds, or scrubbing means video with controls and captions, not a GIF; on a code host, link it from a thumbnail.
- An animation that starts automatically, runs longer than 5 seconds, and sits beside other content must be pausable, stoppable, or hideable (WCAG 2.2.2). A looping GIF meets all three and a README offers no pause control, so wrap it in a collapsible details block so it plays only when opened, make it play once, or link it as video with controls; a static screenshot beside it is a fallback for readers who block motion, not compliance.
- Motion serves feedback, hierarchy, spatial relationship, or state change, never ornament; keep it short and let the reader stop it.

## Designing And Verifying Visuals

- For material that will be presented or demonstrated rather than read alone, show before telling: replace prose that asserts a claim with the artifact that demonstrates it — a screenshot, a diagram, a recording, a real case — and never state a belief or conclusion as a bare line of text when an instance would let the reader reach it themselves. Prefer a capture of the real thing over a drawing of it.
- Keep captured evidence raw: a screenshot, ticket, or terminal capture persuades precisely because it is the real artifact, so crop it for relevance but do not redraw it into a tidy explainer — a recreated or retyped version reads as fabricated and loses the conviction the original carried. When available, let `artifact-hygiene` own required redaction before the capture travels. If the evidence you need does not exist yet, mark it TBD — resolved or cut before the artifact ships, like any TBD; never mock up a fake to fill the gap.
- A before/after comparison supports its claim only when the panels differ in the thing claimed and nothing else: hold theme, crop, dimensions, and state constant and re-capture, rather than pairing whatever images you were handed — otherwise the difference reads as the incidental variable, and a skeptic dismisses a real gain as cosmetic. This is the visual twin of the rule that a number must measure the claim it is cited for.
- Check that a recording is legible at viewing size before making it the main visual. When it is a terminal, dense small text, or a long scroll, make a static or before/after capture the primary visual and demote the recording to optional supporting evidence — a recording the audience cannot read proves nothing, however real it is. Make a capture legible by re-rendering its source at higher zoom and re-capturing natively, never by upscaling a low-resolution crop — interpolation only blurs it further.
- Read "trim this recording" as make it usable, not make it shorter: cut dead waiting time, speed-ramp the exploratory stretch and drop back to real time for the payoff, and crop away tool chrome, cost meters, and status bars that carry nothing for the audience. Say what the recording still cannot do (no audio, unreadable at the back of a room) instead of shipping a shorter version of an unusable one, and confirm frame-by-frame that the footage actually shows the event its caption claims — a caption describing one incident over video of another is worse than no clip.
- Treat sensitive content as a mandatory exclusion, not an editing preference. When available, let `artifact-hygiene` own the full-span frame scan and redaction; use its result to keep every occurrence out of the reader-facing cut. Trust frames over timestamps, since a UI renders streamed content earlier than the log or transcript says it completed.
- Make content legibility the bar; keep decorative styling secondary, and use color only when it encodes meaning (category, severity, diff, or the one element the takeaway names), not as ornament.
- When color carries meaning, pair it with a label, shape, or pattern so it reads without color.
- Encode values by position or length before angle, area, or color; avoid pie, 3D, and dual-axis charts.
- Beyond the form table in `SKILL.md`: correlation is a scatter, a distribution can also be a box plot, and many series that would cross into spaghetti become small multiples on one shared scale.
- Erase chart furniture that carries no data (default gridlines, heavy borders, backgrounds, redundant labels) before styling what remains, and aim attention the way the color rule above does: mute context series to gray and spend one accent color on the element the takeaway title names.
- Start bar and area baselines at zero, and keep visual magnitude proportional to the data.
- Label series directly instead of relying on a legend.
- Put each visual at the exact point where the text argues from it, and draw its conclusion in the adjacent prose — a reader should never scroll between a claim and its evidence, and a figure no sentence argues from is decoration however informative it looks.
- In the fallback path, remember that auto-layout diagrams (e.g. Mermaid) render differently per tool (label width, fonts, rendering mode), so long or CJK-heavy labels can clip — keep diagram labels short. Each of the following rules out auto-layout on its own, no judgement call about whether the engine could still fit it: elements that must hold position while the state around them changes, two or more states of one system shown in a single frame, containers nested inside containers, or three or more visually distinct classes of connection. Shortening labels, splitting into subgraphs, or adding a colour class does not answer any of them — those fix crowding, and crowding is not the problem being described. Author the geometry yourself instead: a fixed viewBox with explicit coordinates, color through variables so both themes work, mutually exclusive states as groups switched by one attribute. Reach for a table when the content is a lookup, not when the diagram is merely hard to lay out — the relationship the diagram existed to show is exactly what a table drops.
- Open every visual this skill owns at its real viewing size and read it as the reader before shipping it: what the eye lands on first, whether every label is legible, whether anything collides, overlaps, or is cut, and whether each line, color, and arrow still means what its key says. Render-only defects are invisible in the source. If no rendering surface is available, say the visual is unverified rather than presenting it as checked. For a diagram owned by `technical-diagramming`, apply this review to the takeaway and surrounding page; leave diagram geometry, connectors, legends, and semantic reading to that skill. Page-level thresholds remain the `verification` skill's job.

## HTML And Interactive Documents

- Design so the page can clear the rendering checks rather than checking them here: readable when zoomed, high enough contrast, and no horizontal scrolling on a narrow screen. The thresholds those become, and the verification of a rendered page against them, belong to the `verification` skill — including the cache-defeating reload that proves you are looking at the version you just edited.
- State where the artifact will run and whether it must work offline before building. When available, let `artifact-hygiene` own packaging the runtime dependencies and proving the handoff satisfies that constraint.
- Surface click-triggered details where the reader is looking — and to hold both readability and authenticity, keep one restateable conclusion in large type — with its primary proving visual, per the adjacency rule — on the surface and demote the full-detail real artifact (a screenshot, report, or recording) to a click-to-open evidence layer opened only when challenged — the click-capable form of show-before-telling, not an exception to it: the real artifact stays one click away.
- When material does not fit the time or space budget, attach it as an explicitly optional item the reader can open on demand instead of deleting it — the click-capable form of the demote-don't-delete rule: label it with wording that permits use ("open it whenever") rather than discouraging it ("we won't cover this"), and give it a click target big enough to hit live.
- Use one canonical visual per flow — when several captures show the same flow, keep the best one and cut the rest.
- For a deck meant to be projected and talked through (not read alone), size it for a room: large type and a generous content area that fills the screen with minimal empty margins, and a navigation menu or anchored sections a presenter can jump between rather than only scrolling top-to-bottom. Design for the venue's real full screen and, when the venue or design is dark-themed, adapt every element to it and tone down glare-bright text; the full-screen, aspect-ratio, and glare verification of the built deck belongs to the `verification` skill.
- Use motion only to aid comprehension — a progressive reveal that paces a dense slide, or an animated build that walks through a process step by step — never as decoration; a static form that reads instantly beats motion that delays the point.
