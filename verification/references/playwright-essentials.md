# Playwright Essentials

The durable practices that keep a Playwright check trustworthy and stable — not a full test-authoring
cookbook. For a large, long-lived spec suite (deep POM, sharding, component/Electron/extension testing,
per-topic recipes) use the project's own Playwright guidance or a dedicated Playwright skill.

## Locators

Prefer user-facing locators (`getByRole`, `getByLabel`, `getByText`), fall back to `getByTestId` when no
semantic locator fits, and treat CSS/XPath as a last resort. Narrow with `filter(...)` and chaining rather
than brittle compound selectors, and assert user-visible behavior, not implementation details.

## Assertions & Waiting

Use web-first `expect(locator)` assertions, which auto-retry; generic `expect(value).toBe(...)` does not.
Never hard-wait (`page.waitForTimeout`, `setTimeout`) — wait on a real signal (`waitForResponse`,
`waitForURL`, `locator.waitFor`), let actions auto-wait, or poll with `expect(...).toPass(...)` /
`expect.poll(...)`.

## Authentication

The single biggest lever for fast, stable auth is **`storageState` reuse** — log in once, save cookies +
localStorage, and start every later test already authenticated. The file may contain cookies or headers that
can impersonate the test account: keep it in an existing ignored auth/output path or a disposable run
directory, and never commit, print, or ship it. Introduce a narrow project ignore convention only when the
maintained suite will reuse the state; otherwise keep the one-off state temporary.

Prefer an API login (`context.request.post('/api/auth/login', ...)`) over driving the login UI when you are not
testing the login flow itself. Only use a fresh, unauthenticated context when the test *is* the login flow.

## Mocking

Choose the mocking boundary from what the test claims to prove.

- A test cannot prove frontend↔backend integration while mocking that boundary. Keep at least one real
  integration path against local dev or staging, and seed data through the API.
- For a UI-focused test that needs a rare error or deterministic edge state, mocking an owned API is valid
  when a separate contract or integration check covers that boundary; state that this test proves the UI
  response, not the integration.
- Mock third-party services you don't own (payments, email, OAuth token exchange, analytics) unless the task
  explicitly tests that integration. Use `page.route()` + `route.fulfill()` / `route.abort()` at the network
  layer instead of stubbing `fetch` in `page.evaluate()` (fragile, doesn't survive navigation).
- For complex external sequences, record/replay with `routeFromHAR`, and re-record when the API changes.

## Isolation & Page Objects

Each test must be independent: no reliance on order, no shared mutable accounts/data across parallel workers;
put per-test setup/teardown in fixtures. Reuse the project's existing Page Objects, and extract one only when
stable locators or flows recur across tests — keep a one-off check local rather than creating an abstraction
for hypothetical reuse.

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
