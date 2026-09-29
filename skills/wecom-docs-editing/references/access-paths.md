# Access paths and credentials

Table of Contents

1. wecom-cli (official, open source)
2. Official WeCom document API
3. Browser session: one login per work session
4. Why no persistent profile and no exported cookie

## wecom-cli (official, open source)

Source: https://github.com/WecomTeam/wecom-cli (MIT), installed with
`npm install -g @wecom/cli`. Everything below was observed on 2026-09-29 with
wecom-cli 1.3.4 against a member-created sheet and two imported ones.

- Auth: `wecom-cli auth init` shows a QR code; scanning it creates a bot in the user's
  name and stores its credential encrypted under the CLI's config directory. Calls run
  as that bot on behalf of the user. Creating and importing documents worked right
  away; reading any document returned errcode 851008 ("partial no authorization") until
  the user granted the bot the document-content permission in WeCom.
- Works: `sheet get` (tab titles and `sheet_id`s), `sheet ranges get` with
  `"mode": "default"` and a range (structured `grid_data`: text, number, link text and
  URL, select value, fonts), `sheet contents update` for text, number, and link cells
  plus bold and font styles, `sheet subsheets add|delete`, and `sheet import` of a
  local `.xlsx` into a new document. All of these worked on a sheet the user created.
- Without `mode`, `sheet ranges get` returned CSV text in a `content` field even when a
  range was passed, although the official skill documents `default` as the default.
- `SELECT` and `CHECKBOX` cells, although the schema lists option colors and a
  multi-select flag: every variant tried (eight shapes, with and without ids, colors,
  and `multiple`) returned errcode 0 and read back empty, and the page showed the cells
  empty. In a column that already had a list validation, the same write left a broken
  cell whose value read back as `[""]`.
- Plain text in a column with a list validation (imported from `.xlsx`) read back as a
  select value, and the page showed it as the chosen option. A value outside the list
  ("urgent" in a high/medium/low column) was stored the same way and shown with a red
  corner marking it invalid; the API gave no warning.
- Text that looks like a number is stored as a number: `007` and `0012` read back and
  displayed as `7` and `12`. A leading apostrophe stays in the cell as a literal
  character. Date-like text (`2026-09-28`, `1/2`, `3-4`) stayed text.
- In an imported sheet, rows written through the API displayed smaller than the
  imported rows (which showed Calibri 11 pt). The read-back reported SimSun 8 pt for
  both, and also for rows of a sheet created in the page, so the read-back font is not
  the displayed font and cannot be used to match styles; check appended rows on a
  screenshot when the look matters.
- No commands for data validation, conditional formats, filters, frozen panes, or
  deleting a document; `doc --help` mentions deletion but lists no such command.
- Import of an `.xlsx` built with openpyxl carried: the list validation (as a
  "reference data" dropdown with no option colors), conditional-format fills (only when
  the fill is set with `bgColor`; an `fgColor`-only fill imported as a rule with no
  visible fill), the frozen header row, the filter (which later grew to cover rows
  written through the API), and IDs in text-formatted cells such as `007`.
- The official `wecomcli-sheet` skill triggers on the same `doc.weixin.qq.com/sheet`
  links as this skill and documents neither the dropped select cells nor the number
  conversion; install the other `wecomcli-*` skills with `npx skills add
  WeComTeam/wecom-cli --skill <names>` and leave that one out.

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
- Observed on 2026-09-29 with `@playwright/cli` 0.1.19: `playwright-cli -s=NAME open
  --headed URL` without `--persistent` keeps the profile in memory, the login worked,
  and closing the session discarded it. Run it from a scratch directory, because it
  writes snapshots and screenshots under `.playwright-cli/` in the working directory.
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
