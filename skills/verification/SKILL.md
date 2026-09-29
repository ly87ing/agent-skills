---
name: verification
description: Prove that a change, fix, deployment, or config edit actually works before calling it done, and decide what counts as evidence for each claim. Use when asked to verify, validate, confirm, smoke-test, or accept a change in a local, test, staging, or deployed environment; to check that a push, deploy, or applied config took effect; to compare behavior before and after a change; to prove a fix in the environment a bug names; to judge whether tests, logs, a screenshot, or a worker's report count as evidence; and for browser evidence — driving Playwright or DevTools, authenticated flows, responsive layouts, interactive HTML, dashboards, decks, fixed-frame overflow, full-screen projection, media inside overlays, a blank or error render being read as a result, a lost authenticated session, or animation timing making a capture false evidence. Not for writing or tidying Playwright test code alone with no evidence to capture, and not for deciding what to change.
---

# Verification

A claim of done names a rung on a delivery ladder, and the evidence in hand has to reach that rung. Two builds recur below and are never interchangeable: the build under test carries the change, and the pre-change build is the same code without it.

## Procedure

1. Lock the target, per the hard gate below. Stop and report when the named environment cannot be reached in the right auth or permission state, when the change is not in it, or when it is in live use and the check could disturb it without the user's go-ahead.
2. Name the rung the claim needs on the delivery ladder.
3. Collect evidence that reaches that rung: the narrowest test that can fail for rung 1, SHA read-backs for rungs 2 and 3, real inputs compared against the pre-change build for rung 4, the consumer's own confirmation for rung 5. Check through the consumer's real path, and for a rendered surface follow the browser section.
4. For delegated work, apply the delegated-work section before repeating anything the worker claims.
5. Report with the template at the end: the rung reached, never a higher one.

## Lock the target before collecting any evidence (hard gate)

- Print the target triple — the build under test (branch, commit, or image), environment, entry address — and the source of each: the bug's environment tag, the user's words, the project profile, or the deployed build id. When the source is a bug's tag or the user's words, that environment is the only acceptable one.
- A reachable but non-equivalent environment is never a substitute. When the named environment is down or unauthenticated, report the blocker and stop; anything measured on a substitute is discarded, never uploaded or written back. Case: a UI fix for a bug tagged with one QA environment was checked on a different reachable site after the named one failed its health check; the user rejected it and every result was thrown away.
- Confirm the change under test is in the target: commit SHA or ancestry, image tag, or file hash. A version endpoint's release string or a release name does not prove the commit is deployed.
- When a fixture, address, or case points at a target that has moved, it is a wrong case to delete, not a failure to rerun. Case: probes kept running against a router address retired months earlier, producing false failures until the cases were removed.
- Do not disturb what is in live use. When the environment, the process, or the agent under test is in the user's hands right now, design the check read-only; if it cannot be read-only, state the impact and stop until the user gives a go-ahead.

## The delivery ladder

| Rung | What proves it | What does not |
| --- | --- | --- |
| 1. Tests green | The narrowest test that exercises the change, its real result read (`BUILD SUCCESSFUL`, `N failed`), and the failing set diffed against the same tests on the pre-change build, reported as "no new failures" | A piped command's exit code (`cmd \| tail` reports tail's status); a pass count; watch-mode output; "all passed" while old failures remain |
| 2. Pushed | After `git fetch`, local HEAD, the tracking branch, and the remote share one SHA; the working tree is clean; every nested sub-repo listed line by line and checked | A `git push` exit code; a clean status at a hub root that ignores nested repos |
| 3. Applied or deployed | The running build carries the commit (SHA, image tag, hash) and the live configuration reads back with the new value | Push success; a version string; an HTTP 200; a "loaded" log line; a config file that exists |
| 4. Verified | The changed behaviour exercised with real inputs and compared against the pre-change build on the same inputs, including the failure branch | Existence checks; deployment checks; status codes; a unit test alone for a behaviour that lives in the deployed system |
| 5. Accepted | The consumer — QA, the user, a downstream team — confirmed through their own path | The agent's own screenshot; a worker's report; a passing exit code; "the code exists on a branch" |

Report the highest rung actually reached and name the next one; lower-rung evidence never stands in for a higher rung. Push success is not deployment success, deployment success is not correctness, and correctness on the internal path is not acceptance.

## Verify behaviour with real inputs and an old-new comparison

1. Take the inputs from the system's own record — access logs, recent requests, real tickets — and pick the highest-frequency shapes plus the boundary the change touches; invented samples miss the shape production actually sends.
2. Exercise the changed path with those inputs on the new build.
3. Run the same inputs against the pre-change build — the previous environment, the previous image, or the change stashed — and diff the outputs.
4. Before attributing a difference to code, rule out data differences between the two sides: does the artifact, row, or fixture exist on both?
5. Include the failure branch: the input that must now be rejected, skipped, or retried, and confirm it is.

Case: a version-decision service was declared verified because eight removed config keys were absent from the deployed package and the pod was Running. Asked whether that was really all the verification amounted to, the check was redone — the top request shapes were pulled from the access log and the API was called with them on both builds — and one platform returned empty on the new build, traced to missing data in that environment rather than to the code.

## Verify through the consumer's real path

- Users reach the service through the external domain, the gateway, and the client; verify there, not only from inside the pod or on localhost. A path that works internally and returns 404 externally has failed.
- Run the check under the affected identity, role, or permission; a privileged account never reproduces an identity-scoped failure.
- Keep every artifact handed over as evidence — a test upload, a probe file — until the consumer has confirmed; cleaning it up early turns your evidence into their false alarm. Case: a test file was deleted right after an internal check passed, the user then opened its external URL, saw 404, and reported a defect that did not exist. Placement and eventual cleanup of such artifacts belong to `artifact-hygiene`.

## Evidence from delegated work

- A worker's status line, its screenshot file, its "tests pass", or a passing exit code is a claim, not acceptance. Re-run the decisive check, read the diff, and drive the surface yourself.
- Before handing delegated implementation to the user, check that the user can use it end to end: it builds, it is packaged or downloadable where the user expects it, and the usage note exists. Case: a delegated implementation stopped at "server capability done", and the user had to ask for the CLI, the binaries, the download page, and the build script one by one. That check is yours, so it cannot reach rung 5: report the work as accepted only after the consumer confirms it through their own path.
- Keeping audit sub-agents read-only, and checking afterwards that nothing was committed or pushed under your identity, belongs to `change-discipline`.

## Browser and rendered-surface evidence

1. Define the UI surface.
   - Identify the route, the state, the interaction, the data boundary, the target viewports and breakpoints, and the user-visible success criteria the check has to demonstrate.
   - Validate dynamic or external data at its boundaries, so a missing or malformed feed is read as a data defect rather than a layout one.
2. Choose the browser tool by intent.
   - Use Playwright for reproducible assertions, regression coverage, route/network mocking, and CI-stable automation.
   - Use Chrome DevTools for one-off visual inspection, layout/scroll diagnosis, performance traces, Core Web Vitals, request waterfalls, cache/timing analysis, memory, and low-level WebSocket inspection.
   - Use a session-aware browser when the task needs navigation, auth, forms, scraping, or profile/session reuse.
   - For locator design, web-first assertions, storageState auth, mocking boundaries, isolation, and flaky-test triage, apply [references/playwright-essentials.md](references/playwright-essentials.md); for a large, long-lived spec suite (deep Page Object Model, sharding, component/Electron testing), follow the project's existing Playwright conventions.
   - When a Playwright run fails before it reaches the app because the runner, browser, download, or media helper cannot start, apply [references/playwright-toolchain.md](references/playwright-toolchain.md) instead of reading that failure as UI evidence.
   - Before hand-rolling authentication, captcha-solving, or a login flow, search the project for an existing login or verification harness and reuse it. Projects that need browser verification often already ship a tested one (zero-touch auth entry, slider/image-captcha solver, MFA/TOTP), and reinventing it in DevTools or by vision is brittle and wastes turns. Hand-drive the browser only when the project genuinely has no such helper.
3. Preserve authenticated context deliberately.
   - Do not assume a fresh isolated browser has the required cookies, profile, or permissions.
   - To recover an authenticated session you lost (a dropped connection, an extension seizing the tab), open a new tab in the same profile so the cookies and login carry over; do not relaunch a fresh or isolated context, which discards the auth. Confirm with the user before any relaunch that could touch account state.
   - A blank or error render is a load failure, not a result: never read a prior mutating action's success or failure off it, and re-verify the outcome from an independent record before retrying or reporting.
   - When a mutating flow is interrupted, assume the server-side record (a case, order, or ticket) may already exist: re-query it and resume by its id rather than restarting the flow, which risks a duplicate submission.
   - If a browser tool cannot start, connect, or attach, report that tool failure before falling back.
   - When the user has removed the blocker — logged you in, granted access, opened the tool for you — carry the real interaction through to completion and capture the evidence (the live run, its screenshots, or the recording); do not stall or substitute a written description for the actual interaction the task called for.
4. Do not replace regression coverage with inspection. DevTools and session browsers diagnose and execute; a durable user-visible bug needs the smallest relevant Playwright or project-native check unless the user asked only for an ad hoc look.
5. Verify interactive HTML before done.
   - Clear the thresholds a rendered page has to meet: type still readable at 200% zoom, contrast of at least 4.5:1 for body text and 3:1 for large text and chart elements, no horizontal scrolling at a 320px width, adequate hit areas, and accessible modal and focus behaviour.
   - For exploratory master-detail interfaces, drive a repeated inspect-return-inspect flow and verify that opening detail does not discard task-relevant exploration state or leave keyboard focus stranded.
   - Load the rendered output, check console errors, key elements, and interactions, and capture a screenshot of the decisive state.
   - When re-verifying a local file you just edited, hard-reload with the cache disabled; otherwise a stale cache shows the previous version and you verify the edit you did not make.
   - For anything rendered into a fixed frame (slides, cards, fixed-aspect canvases), check every instance for overflow and clipping at the target size — content that fits while drafting silently overflows the frame, and the clipped part is invisible to its author.
   - For a deck or page that will be projected, verify at OS-level full screen at the venue's aspect ratio (16:9) — a browser window's inline "full screen" is not the venue's — stepping through every page for leftover margins, overflow, and broken layout; when the venue is dark, also check for glare-bright text that dazzles in a dark room.
   - When playable media sits inside a click-to-dismiss overlay, stop the media's own clicks from reaching the dismiss handler and pause playback on close; otherwise the first click on the controls dismisses the overlay, and a dismissed overlay keeps playing.
   - Where a container binds global keys or screen zones to navigation, decide explicitly which keys belong to focused media, then drive it: confirm that clicking content does not navigate, and that a focused player or embedded frame has not swallowed the keys the reader needs.
6. Capture what is actually rendered.
   - Settle animations before capturing: force or wait out entrance, staggered, and scroll-triggered motion, or the capture shows partial content and stands as false evidence of the rendered layout. Wait for images to finish decoding too, because a capture taken mid-decode shows blank or black regions.
   - Treat a defect that appears only in such an early capture as a phantom: re-capture and confirm it is real before editing the page, or you will "fix" a correct page against a false screenshot.
   - For an SVG handed over as a file or inline in a page (save an inline one to a file), run `python3 scripts/validate_svg.py <file>`: it catches malformed XML, a missing or invalid viewBox, duplicate IDs, broken local references, and non-local dependencies, but cannot prove layout, legibility, accessibility, or factual correctness, so still read the real render at its viewing size.
   - Read what is on screen from the pixels, not from the log, transcript, or DOM text that produced them — a UI renders streamed content progressively, so a timestamp marks when a message completed, not when it first became visible. When it matters what a viewer could see and when, extract frames and check them.
   - State what a capture does not cover before handing it over as evidence.

## Report

Fill every line; write `none` rather than dropping one.

```text
claim: <what is being called done>
rung reached: <1-5 and its name>; next rung: <name, and what would prove it>
target: <build under test> on <environment> at <entry address>; sources: <bug tag, user's words, profile, build id>
evidence: <check run -> result read>, one line each
inputs: <where they came from; how many; which failure-branch input>
pre-change comparison: <build compared, differences and their cause> | not run: <why>
not covered: <states, sizes, paths, identities, and consumers not exercised, and why>
```

A screenshot proves one state at one size, not the flow around it, and a recording of a passing run is not a regression test; say so under `not covered` when either is offered as evidence.

`reader-facing-writing` owns why a visual is needed; `artifact-hygiene` owns where evidence files live and when they are cleaned up; `change-discipline` owns what to change and why before verification starts.
