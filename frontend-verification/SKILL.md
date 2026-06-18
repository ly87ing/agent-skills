---
name: frontend-verification
description: Validate frontend outcomes, browser automation, UI flows, accessibility-relevant states, interactive HTML, dashboards, decks, and reader-facing web artifacts. Use when deciding or proving the verification strategy for UI behavior, browser evidence, DevTools diagnosis, authenticated flows, responsive layouts, or HTML deliverables. For detailed Playwright test implementation or flake debugging, use playwright-best-practices instead.
---

# Frontend Verification

## Workflow

1. Define the UI surface.
   - Identify the route, state, interaction, data boundary, and user-visible success criteria.
   - Validate dynamic or external data at boundaries.
2. Choose the browser tool by intent.
   - Use Playwright for reproducible assertions, regression coverage, route/network mocking, and CI-stable automation.
   - Use Chrome DevTools for one-off visual inspection, layout/scroll diagnosis, performance traces, Core Web Vitals, request waterfalls, cache/timing analysis, memory, and low-level WebSocket inspection.
   - Use a session-aware browser when the task needs navigation, auth, forms, scraping, or profile/session reuse.
   - Use `playwright-best-practices` for detailed Playwright test architecture, locator design, fixture setup, flaky-test debugging, or test implementation patterns.
3. Preserve authenticated context deliberately.
   - Do not assume a fresh isolated browser has the required cookies, profile, or permissions.
   - If a browser tool cannot start, connect, or attach, report that tool failure before falling back.
4. Do not replace regression coverage with inspection.
   - DevTools and session browsers diagnose and execute tasks; durable user-visible bugs need the smallest relevant Playwright or project-native check unless the user asked only for ad hoc investigation.
5. Verify interactive HTML before done.
   - Use scalable text, adequate hit areas, accessible modal/focus behavior, and one canonical visual per flow.
   - Match online/offline dependency strategy to where the artifact will run.
   - Load the rendered output, check console errors, key elements, interactions, and a screenshot.

## Stop Conditions

- The page cannot be reached in the right auth or permission state.
- The screenshot or browser state does not match the claimed user flow.
- A one-off visual check is being used as proof of durable regression coverage.
- The task is only about writing or debugging Playwright test code, with no UI evidence or verification-strategy decision to make.
