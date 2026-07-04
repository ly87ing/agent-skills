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
