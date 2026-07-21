---
name: frontend-verification
description: Validate frontend outcomes, browser automation, UI flows, accessibility-relevant states, interactive HTML, dashboards, decks, and reader-facing web artifacts. Use when deciding or proving the verification strategy for UI behavior, browser evidence, DevTools diagnosis, authenticated flows, or responsive layouts. Also use when an interrupted mutating flow may already have created the record, when a blank or error render is being read as a result, when a lost authenticated session must be recovered without discarding its cookies, when animation or image-decode timing can make a capture false evidence, and for checking a built page or deck for fixed-frame overflow, its rendering at the venue's full screen, and media or key handling inside overlays. For durable Playwright practices (locators, web-first assertions, storageState auth, mocking, flaky triage, and browser-install/toolchain failures), see references/playwright-essentials.md; for a large spec suite, follow the project's native Playwright guidance.
---

# Frontend Verification

## Workflow

1. Define the UI surface.
   - Identify the route, state, interaction, data boundary, target viewports/breakpoints, and user-visible success criteria.
   - Validate dynamic or external data at boundaries.
2. Choose the browser tool by intent.
   - Use Playwright for reproducible assertions, regression coverage, route/network mocking, and CI-stable automation.
   - Use Chrome DevTools for one-off visual inspection, layout/scroll diagnosis, performance traces, Core Web Vitals, request waterfalls, cache/timing analysis, memory, and low-level WebSocket inspection.
   - Use a session-aware browser when the task needs navigation, auth, forms, scraping, or profile/session reuse.
   - For locator design, web-first assertions, storageState auth, mocking boundaries, flaky-test triage, and browser-install/toolchain failures that stop a run before it reaches the app, apply `references/playwright-essentials.md`; for a large, long-lived spec suite (deep Page Object Model, sharding, component/Electron testing), follow the project's existing Playwright conventions.
   - Before hand-rolling authentication, captcha-solving, or a login flow in the browser tool, search the project for an existing login/verification harness or helper and reuse it. Projects that need browser verification often already ship a tested one (zero-touch auth entry, slider/image-captcha solver, MFA/TOTP), and reinventing it in DevTools or by vision is brittle and wastes turns. Hand-drive the browser only when the project genuinely has no such helper.
3. Preserve authenticated context deliberately.
   - Do not assume a fresh isolated browser has the required cookies, profile, or permissions.
   - To recover control of an authenticated session you lost (a dropped connection, an extension seizing the tab), open a new tab in the same profile so the cookies and login carry over — do not relaunch a fresh or isolated context, which discards the auth; confirm with the user before any relaunch that could touch account state.
   - A blank or error render is a load failure, not a result: never read a prior mutating action's success or failure off it, and re-verify the outcome from an independent record before retrying or reporting.
   - When a mutating flow is interrupted, assume the server-side record (a case, order, or ticket) may already exist: re-query it and resume by its id rather than restarting the flow, which risks a duplicate submission.
   - If a browser tool cannot start, connect, or attach, report that tool failure before falling back.
   - When the user has removed the blocker — logged you in, granted access, or opened the tool for you — carry the real interaction through to completion and capture the evidence (the live run, its screenshots, or the recording); do not stall or substitute a written description for the actual interaction the task called for.
4. Do not replace regression coverage with inspection.
   - DevTools and session browsers diagnose and execute tasks; durable user-visible bugs need the smallest relevant Playwright or project-native check unless the user asked only for ad hoc investigation.
5. Verify interactive HTML before done.
   - Use scalable text, adequate hit areas, accessible modal/focus behavior, and one canonical visual per flow.
   - Match online/offline dependency strategy to where the artifact will run.
   - Load the rendered output; check console errors, key elements, and interactions; and capture a screenshot.
   - When re-verifying a local file you just edited, hard-reload with the cache disabled; otherwise a stale cache shows the previous version and you verify the edit you did not make.
   - For anything rendered into a fixed frame (slides, cards, fixed-aspect canvases), check every instance for overflow and clipping at the target size — content that fits while drafting silently overflows the frame, and the clipped part is invisible to its author.
   - For a deck or page that will be projected, verify at OS-level full screen at the venue's aspect ratio (16:9) — a browser window's inline "full screen" is not the venue's — stepping through every page for leftover margins, overflow, and broken layout; when the venue is dark, also check for glare-bright text that dazzles in a dark room.
   - When playable media sits inside a click-to-dismiss overlay, stop the media's own clicks from reaching the dismiss handler and pause playback on close; otherwise the first click on the controls dismisses the overlay, and a dismissed overlay keeps playing.
   - Where a container binds global keys or screen zones to navigation, decide explicitly which keys belong to focused media, then drive it: confirm that clicking content does not navigate, and that a focused player or embedded frame has not swallowed the keys the reader needs.

## Captured Media As Evidence

- Settle animations before capturing: force or wait out entrance, staggered, and scroll-triggered motion, or the capture shows partial content and stands as false evidence of the rendered layout. Wait for images to finish decoding too — a capture taken mid-decode shows blank or black regions. Treat a defect that appears only in such an early capture as a phantom: re-capture and confirm it is real before editing the page, or you will "fix" a correct page against a false screenshot.
- Read what is actually on screen from the pixels, not from the log, transcript, or DOM text that produced them — a UI renders streamed content progressively, so a timestamp marks when a message *completed*, not when it first became visible. When it matters what a viewer could see and when, extract frames and check them.
- State what a capture does not cover. A screenshot proves one state at one size; it is not evidence for the flow around it, and a recording of a passing run is not a regression test.

## Stop Conditions

- The page cannot be reached in the right auth or permission state.
- The screenshot or browser state does not match the claimed user flow.
- A one-off visual check is being used as proof of durable regression coverage.
- A login or captcha flow is being hand-implemented in the browser tool while the project already ships a login/verification helper for it.
- The task is only about writing or debugging Playwright test code, with no UI evidence or verification-strategy decision to make.
