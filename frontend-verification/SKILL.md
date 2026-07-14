---
name: frontend-verification
description: Validate frontend outcomes, browser automation, UI flows, accessibility-relevant states, interactive HTML, dashboards, decks, and reader-facing web artifacts. Use when deciding or proving the verification strategy for UI behavior, browser evidence, DevTools diagnosis, authenticated flows, responsive layouts, or HTML deliverables. For the durable Playwright practices that keep a check stable (locators, web-first assertions, storageState auth, mocking boundaries, flaky triage), see references/playwright-essentials.md; for a large, long-lived spec suite, follow the project's native Playwright guidance.
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
   - For locator design, web-first assertions, storageState auth, mocking boundaries, and flaky-test triage, apply `references/playwright-essentials.md`; for a large, long-lived spec suite (deep Page Object Model, sharding, component/Electron testing), follow the project's existing Playwright conventions.
   - Before hand-rolling authentication, captcha-solving, or a login flow in the browser tool, search the project for an existing login/verification harness or helper and reuse it. Projects that need browser verification often already ship a tested one (zero-touch auth entry, slider/image-captcha solver, MFA/TOTP), and reinventing it in DevTools or by vision is brittle and wastes turns. Hand-drive the browser only when the project genuinely has no such helper.
3. Preserve authenticated context deliberately.
   - Do not assume a fresh isolated browser has the required cookies, profile, or permissions.
   - If a browser tool cannot start, connect, or attach, report that tool failure before falling back.
   - When the user has removed the blocker — logged you in, granted access, or opened the tool for you — carry the real interaction through to completion and capture the evidence (the live run, its screenshots, or the recording); do not stall or substitute a written description for the actual interaction the task called for.
4. Do not replace regression coverage with inspection.
   - DevTools and session browsers diagnose and execute tasks; durable user-visible bugs need the smallest relevant Playwright or project-native check unless the user asked only for ad hoc investigation.
5. Verify interactive HTML before done.
   - Use scalable text, adequate hit areas, accessible modal/focus behavior, and one canonical visual per flow.
   - Match online/offline dependency strategy to where the artifact will run.
   - Load the rendered output; check console errors, key elements, and interactions; and capture a screenshot.

## Stop Conditions

- The page cannot be reached in the right auth or permission state.
- The screenshot or browser state does not match the claimed user flow.
- A one-off visual check is being used as proof of durable regression coverage.
- A login or captcha flow is being hand-implemented in the browser tool while the project already ships a login/verification helper for it.
- The task is only about writing or debugging Playwright test code, with no UI evidence or verification-strategy decision to make.
