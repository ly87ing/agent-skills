# Playwright Essentials

The durable practices that keep a Playwright check trustworthy and stable. This is the small,
cross-cutting core that matters whenever you drive Playwright for verification — not a full test-authoring
cookbook. For a large, long-lived spec suite (deep POM, sharding, component/Electron/extension testing,
per-topic recipes) use the project's own Playwright guidance or a dedicated Playwright skill.

## Table of Contents

1. [Locators: prefer user-facing, resilient selectors](#locators)
2. [Assertions & waiting: web-first, never hard-wait](#assertions--waiting)
3. [Authentication: reuse storageState](#authentication)
4. [Mocking: mock at the boundary only](#mocking)
5. [Test isolation & Page Objects](#isolation--page-objects)
6. [Flaky tests: find the root cause, don't add retries](#flaky-tests)
7. [Toolchain & browser install: prove the runner can start](#toolchain--browser-install)

## Locators

Pick the most resilient locator available, in this order:

1. **Role** — `getByRole('button', { name: 'Submit' })` (matches what users and assistive tech perceive)
2. **Label** — `getByLabel('Email')`, `getByPlaceholder(...)`
3. **Text** — `getByText(...)`, `getByTitle(...)`
4. **Test id** — `getByTestId('submit-btn')` when no semantic locator fits
5. **CSS / XPath** — last resort only

Narrow with `filter({ hasText })` / `filter({ has })` and chaining instead of brittle compound selectors.

Anti-patterns: `page.locator('.btn-primary')` / `#dynamic-id-123` (breaks on restyle/rerender), and asserting
on implementation details instead of user-visible behavior.

## Assertions & Waiting

Use **web-first assertions** — `expect(locator)` auto-retries until the condition holds or times out:

```typescript
await expect(page.getByRole('heading')).toHaveText('Welcome');
await expect(page.getByRole('button', { name: 'Save' })).toBeEnabled();
await expect(page).toHaveURL(/\/dashboard/);
```

Generic `expect(value).toBe(...)` does **not** retry — use it only for non-UI values.

**Never hard-wait.** `page.waitForTimeout(ms)` / `setTimeout` are the #1 source of flake and slowness. Instead:

- Let actions auto-wait (`click`/`fill` wait for attached, visible, stable, enabled).
- Wait on a real signal: `waitForResponse('**/api/...')`, `waitForURL(...)`, `locator.waitFor({ state })`.
- Poll a condition with `expect(...).toPass(...)` or `expect.poll(...)` rather than a manual retry loop.

## Authentication

The single biggest lever for fast, stable auth is **`storageState` reuse** — log in once, save cookies +
localStorage, and start every later test already authenticated:

```typescript
// once: capture the session
await page.goto('/login');
await page.getByLabel('Username').fill(user);
await page.getByLabel('Password').fill(pass);
await page.getByRole('button', { name: 'Log in' }).click();
await page.context().storageState({ path: '.auth/session.json' });

// config: every test starts logged in
use: { storageState: '.auth/session.json' }
```

Prefer an API login (`context.request.post('/api/auth/login', ...)`) over driving the login UI when you are not
testing the login flow itself. Only use a fresh, unauthenticated context when the test *is* the login flow.

## Mocking

**Mock at the boundary, test your stack end-to-end.**

- **Never mock your own frontend↔backend API.** Mocking it means tests pass while the app breaks — zero
  integration coverage. Hit the real API against local dev or staging; seed data through it.
- **Always mock third-party services you don't own** (payments, email, OAuth token exchange, analytics) with
  `page.route()` + `route.fulfill()` / `route.abort()`. Intercept at the network layer, not by stubbing `fetch`
  in `page.evaluate()` (fragile, doesn't survive navigation).
- For complex external sequences, record/replay with `routeFromHAR`, and re-record when the API changes.

## Isolation & Page Objects

- Each test must be independent: no reliance on order, no shared mutable accounts/data across parallel workers.
- Put per-test setup/teardown in fixtures; don't leak state between tests.
- Encapsulate a page's locators and interactions in a Page Object so a UI change updates one place, and tests
  read as intent (`loginPage.login(email, pass)`) rather than raw selectors.

## Flaky Tests

A retry that goes green is not a fix — it hides a real defect. Classify first, then remediate:

| Category | Symptom | Usual cause |
| --- | --- | --- |
| UI-driven | element not found / click missed | missing wait, animation, dynamic render |
| Environment-driven | CI-only failure | slower CPU, memory limits, cold browser start |
| Data/parallelism | fails with >1 worker | shared backend data, reused accounts |
| Test-suite | fails only after other tests | leaked state, order dependency |

Reproduce with `--repeat-each=N` and `--workers=1` to isolate parallelism, and capture evidence with
`trace: 'on-first-retry'`, `video: 'retain-on-failure'`, `screenshot: 'only-on-failure'`. Fix the underlying
race/isolation problem; treat "flaky infra" as a bug in the service, not a reason to loosen the test.

## Toolchain & Browser Install

A run that never launched a browser proves nothing about the app. When a check fails at startup, fix the runner
before reading anything into the result — and diagnose the toolchain as rigorously as the app, because its
failure modes invite confident misattribution.

- **A browser directory is not an installed browser.** Playwright marks a finished install with an
  `INSTALLATION_COMPLETE` file inside the browser directory, and every `playwright install` reclaims any browser
  directory missing that marker (or unreferenced by a linked installation), logging `Removing unused browser at
  ...`. So an interrupted download leaves a directory that *looks* installed, fails at launch, and then silently
  disappears during the next install — which is easily misread as "the installer deleted my working browser."
  Check for the executable or the marker file, never for the directory.
- **Silence is not a hang — resist the urge to kill the install.** Playwright downloads each archive to
  `$TMPDIR/playwright-download-*/` and only populates the browser cache afterwards, so the cache stays near-empty
  for the whole download. Worse, when a download host is unreachable Playwright waits out a **30s per-host socket
  timeout with no output and no CPU** before retrying a fallback host (`cdn.playwright.dev` →
  `playwright.download.prss.microsoft.com`) — an install that is quietly recovering looks exactly like a dead one.
  Watch the growing zip in `$TMPDIR/playwright-download-*/`, and probe host reachability with `curl -I` on the
  URL in the log; do not infer "stuck" from a quiet log, an empty cache dir, or 0% CPU on Playwright's own
  processes (which cannot see work done by extraction or OS security scanning anyway).
- **Never kill an install mid-write — a truncated binary is worse than a missing one.** The file ends up present,
  correctly named, executable, and still identified as a valid Mach-O/ELF by `file`, so every existence check
  passes; but the kernel `SIGKILL`s it at exec (exit **137**, zero output), and a feature that shells out to it —
  video recording via `ffmpeg` — hangs indefinitely instead of failing. Compare the installed file's byte size
  against the copy inside the downloaded archive to confirm; an interrupted install is repaired by extracting the
  already-downloaded, `unzip -t`-verified archive over it, not by re-downloading.
- **Reaching for a mirror is usually the wrong move** — Playwright already retries its own fallback host, so a
  blocked primary resolves itself if you wait. If you do set `PLAYWRIGHT_DOWNLOAD_HOST`, first check the mirror
  carries the layout your version fetches: recent Playwright pulls Chrome for Testing from
  `builds/cft/<version>/<platform>/chrome-<platform>.zip`, and a mirror lacking that path 404s *and* leaves the
  cache empty (seen with npmmirror against Playwright 1.58.2), turning a slow install into a broken one.
- **Fallback: drive a browser that is already installed** via `channel: 'chrome'` (also set `video: 'off'` when
  `ffmpeg` is missing, so a recording error cannot surface in place of the real failure). Keep the override
  *outside* the repo — a throwaway config that `require`s the committed one and spreads over `use` — so an
  emergency workaround never lands in version control.

**Never read an exit code through a pipe.** `cmd | tail` reports `tail`'s status, so a failed install or test
run happily prints `exit 0`. Redirect instead (`cmd > log 2>&1; echo "EXIT=$?" >> log`), and confirm success
from the artifact that proves it — the browser binary on disk, the suite's own result file — never from a
directory existing or a status line alone.
