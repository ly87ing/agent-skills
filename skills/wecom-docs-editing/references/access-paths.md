# Access paths and credentials

## Official WeCom document API

Checked against the official pages on 2026-09-23.

- Scope rule, from the document API overview
  (https://developer.work.weixin.qq.com/document/path/97392): an app can read and edit
  only the documents it created itself and cannot edit documents created by members; the
  document id is returned only at creation.
- Spreadsheet editing (https://developer.work.weixin.qq.com/document/path/101168):
  `wedoc/spreadsheet/batch_update` accepts one operation per request object, of four
  kinds - add sheet, update range, delete rows or columns, delete sheet. There is no
  request type for data validation, conditional formatting, filters, or frozen panes.
- Calling it needs the access token of a self-built app listed as allowed to call the
  document API, or of a third-party or agent-developed app that holds the document
  permission.
- Use this path when a connector for it exists in the project and the sheet was created
  by that app. It needs no browser and runs unattended, but it cannot touch a sheet a
  person created, which is the common case.

## Browser session: one login per work session

- Launch the automation browser on a temporary profile. With the Chrome DevTools MCP
  server that is its `--isolated` flag: a fresh user-data directory per browser,
  removed when the browser closes. No dedicated server entry is needed.
- The first page load shows the enterprise login page; the user completes it once in
  that window, with the WeCom quick login or a QR code. The whole work session reuses
  it. It ends when the browser closes, or earlier on expiry, a logout elsewhere, a
  password change, or an admin policy; the session lifetime is not published, so do not
  promise one.
- Keep the window visible for the login, because a headless browser cannot show the
  login page to the user. After the login the user can minimize it.
- Observed on 2026-09-23 on macOS with chrome-devtools-mcp 1.9.0: the browser is
  launched with `--disable-backgrounding-occluded-windows`,
  `--disable-background-timer-throttling`, and `--disable-renderer-backgrounding`.
  With the window minimized (confirmed through the operating system's window state),
  `state`, `verify`, toolbar and menu clicks, and the validation dialog all kept
  working, and the window was never brought to the front. The page itself kept
  reporting `visibilityState` "visible" and `hasFocus()` true, so confirm a minimized
  window through the operating system or the user, not the page.
  The temporary profile sat in the per-user temp folder with owner-only permissions, and
  Time Machine excluded it.
- Attaching to the user's everyday browser avoids the login but exposes every open tab
  and every site session to the automation; do it only when the user asks for it.

## Why no persistent profile and no exported cookie

- A WeCom web session cookie grants at least the account's document access, with no
  scope the user can narrow.
- The same launcher also passes `--use-mock-keychain` and `--password-store=basic`
  (observed), so cookies in its profile are encrypted with a fixed key rather than the
  operating system's keychain. A profile kept between sessions would therefore hold a
  practically readable credential on disk, and a home-directory cache location is
  included in backups by default. A temporary profile limits that exposure to the
  hours of one work session.
- Exporting the cookie into a file or environment variable makes the same credential
  portable, and a cookie replayed outside the browser that issued it can be rejected or
  invalidated at unpredictable times.
- While the browser runs, its temporary profile is the credential: do not copy it or
  attach it to a report. The login ends when that browser exits; tell the user they can
  end it early by quitting that browser instance once the work is done.
