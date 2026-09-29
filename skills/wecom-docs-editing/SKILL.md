---
name: wecom-docs-editing
description: "Writes, formats, and verifies WeCom Docs online spreadsheets (doc.weixin.qq.com/sheet): writes rows via wecom-cli, reads every cell back, sets colored dropdowns, conditional formats, filters, and frozen rows in a logged-in browser. Use when the target is a live WeCom sheet other people share."
---

# WeCom Docs Editing

Put data and formatting into a WeCom Docs online spreadsheet that other people read,
and prove every cell landed where it should. A shared sheet is read by people who never
see this session, so a column shifted by one stray tab, or a rule that silently matched
nothing, does more damage than a write that visibly failed. Treat every "accepted"
signal - an API `errcode` 0 or a page toast - as a hint and a cell-by-cell read-back as
the only proof.

Scope is the spreadsheet editor at `doc.weixin.qq.com/sheet/...`. Documents (`/doc/`),
smart sheets (`/smartsheet/`), and smart pages belong to the official `wecomcli-doc`,
`wecomcli-smartsheet`, and `wecomcli-smartpage` skills; hand those over, or, when they
are not installed, say this skill does not cover them and stop. Do not use the official
`wecomcli-sheet` skill for this scope: its documented flow writes select cells the API
silently drops and does not warn that leading-zero IDs turn into numbers.

## Choose the access path

- **Data goes through `wecom-cli`** (`sheet get`, `sheet ranges get`, `sheet contents
  update`, `sheet subsheets add|delete`, `sheet import`). It writes member-created
  sheets as the authorized user and reads cells back as structured values, with no
  browser. What it can and cannot do, as observed, is in
  [references/access-paths.md](references/access-paths.md).
- **Formatting goes through a browser session** logged in as the user: colored
  dropdowns, conditional formats, filters, and frozen rows have no API. Skip the browser
  entirely when the task is data only.
- **A brand-new table** that the user wants as a new document can be built as a local
  `.xlsx` and imported with `sheet import`; the import carries list validations,
  conditional-format fills, the frozen header, the filter, and text-formatted IDs. It
  creates a new document, so never use it to replace a sheet that already exists.
- When `wecom-cli` is missing or unauthorized and the user does not want to set it up,
  fall back to the browser write path (`paste` and `verify` in `scripts/sheet_js.py`),
  described in [references/ui-recipes.md](references/ui-recipes.md).

## Session and credentials

- **CLI.** `wecom-cli auth show --status` must print `authorized`; otherwise run
  `wecom-cli auth init --noninteractive`, give the user the QR link it prints, and wait.
  Reading needs the bot's document-content permission: error 851008 means the user must
  grant it in WeCom (Workbench, Smart robots, the bot, usable permissions); give that
  path rather than retrying. The CLI keeps its credential encrypted; never print it.
- **Browser**, only for formatting. Drive an automation instance on a temporary
  profile, so the session cookie lives only as long as that browser; if the only
  instance keeps a persistent profile, say the login would stay on disk and ask first.
  Open the sheet URL at a window width of about 1600 px or more (a narrower toolbar
  folds the Data menu into a submenu), run `python3 scripts/sheet_js.py state`, and
  evaluate it. If `loginPage` is true, ask the user to log in there (quick login or QR
  code) and wait; never type a password. Keep the browser open until the formatting is
  done, then close it. Never export, store, print, or inject cookies or tokens.
- If the toolbar is missing or disabled, or a CLI write returns a permission error, the
  account can only view the sheet: stop and report that.

## Workflow

1. **Lock the target.** Record the sheet URL, document title, the sheet tab's title and
   its `sheet_id` from `wecom-cli sheet get --json '{"docid": URL}'`, the anchor cell,
   and the source of the rows. Put the block in a JSON or CSV file in a scratch
   location, not in any repository: a list of rows, or `{"rows": [...], "links":
   [[row, col, url], ...]}` with zero-based positions inside the block. When the source
   carries a URL per row (a ticket or wiki link), put it as a link on that row's ID or
   title cell by default instead of a column of raw URLs. For each column that will get
   a dropdown in step 5, list its distinct values and ask before writing when two of
   them differ only by spaces, full- or half-width characters, or wording for the same
   state ("done" and "completed"): the dropdown makes each distinct value its own
   option, so an unmerged variant splits one state across two filter entries.
2. **Look before writing.** Get the read-back range from `python3 scripts/cli_grid.py
   range --input BLOCK --anchor B2`, save `wecom-cli sheet ranges get --json '{"docid":
   ..., "sheet_id": ..., "range": RANGE, "mode": "default"}'` to a file, and run
   `cli_grid.py verify --input BLOCK --anchor B2 --readback FILE --blank`. Always pass
   `"mode": "default"`: without it the response is CSV text with no cell structure, and
   an empty-looking parse of it once hid a sheet full of data. `ok: true` means the
   footprint and its right and bottom borders are empty. When resuming interrupted
   work, run the full `verify` first and skip the write if the block is already there
   exactly. Anything else is someone's data: show the non-empty cells and ask.
3. **Write.** Run `cli_grid.py request --input BLOCK --anchor B2 --docid DOC --sheet-id
   ID` and pass its output to `wecom-cli sheet contents update --json`. It writes every
   cell as text or link. Never write `SELECT` or `CHECKBOX` cells: the API returns
   success and drops the value in a plain column, and blanks the cell in a dropdown
   column. Plain text written into a column with a list validation became that option
   (observed on an imported one), but a value outside the list was stored too and only
   marked invalid on the page, so check values against the column's options first. `request` warns about number-like text
   (`007`, `1.50`, 16+ digits): the sheet stores it as a number and reads it back
   changed. Tell the user before writing and let them choose; there is no API cell
   format that keeps it as text.
4. **Verify.** Read the same range back with `"mode": "default"` and run `cli_grid.py
   verify` with the same block and anchor. Require `ok: true`: every cell equal, every
   link URL equal, nothing spilled past the block. Report any diff as found; do not
   retry silently.
5. **Format.** Give every column this session writes whose values repeat from a short
   fixed vocabulary (status, priority, result, grade, yes/no) a colored dropdown by
   default, even when the user asked only for the data: each value carries its color,
   the column filters by option, and the page flags values outside the list. Color by
   meaning (bad red, at risk yellow or orange, good green, not applicable gray) and
   state the mapping in the report. One value keeps one color across columns and tabs:
   read the colors of dropdowns already in the sheet with `dialog-readback` and reuse
   them. Leave names, dates, numbers, IDs, and free text as plain cells; use conditional
   formatting for their rules and for formula rules. When the write created a new table
   with a header row in a blank area, also freeze the header row and add a filter over
   header plus data by default; a filter with no condition set hides no rows. On a table
   that was already there, add them on request. This step needs the browser. After each
   change, read it back through its own surface - `dialog-readback` on a corner cell and
   on a cell just outside the range for dropdowns, `state` for the filter and frozen
   rows. For a conditional format, a rule in the list is not proof it works: count from
   the source data how many cells in the apply range it should color, then require `ok:
   true` from `cf-matches --range K2:K77 --sheet TAB --expect N`. A rule that colors
   fewer or more cells than that is a failed rule to fix, not a finished one. Click
   paths, labels, and the palette are in [references/ui-recipes.md](references/ui-recipes.md).
6. **Report.** State the tab and range written, cells compared, the diff count, links
   checked, each formatting change with its read-back (for a conditional format, the
   cells it colors against the count expected), and what was not verified.

## Stop and ask

- Before overwriting non-empty cells, deleting or replacing rules, validations, tabs,
  or documents that this session did not create, or clearing the whole sheet's rules.
  The delete-all confirmation states a rule count; proceed only when it equals what this
  session made.
- Before a change the user did not ask for that alters what collaborators see, such as
  a filter that hides rows, a sort, or a dropdown on columns this session did not
  write. A filter the user asked for, or the condition-free default of step 5, is
  added directly. Either way, whether a filter is shared with collaborators could not
  be established from the page, so describe that risk in the report instead of
  asserting either way.
- After adding a dropdown, values outside its list become invalid; say so.
- When a label or element is missing, `menu-pick` returns the visible menu items. Stop
  and report them; do not guess by screen coordinates, because a changed page makes a
  guessed click land on the wrong control.
- Close every dialog opened only for reading: `dialog-readback` cancels by default.
- Test in a new tab added with `sheet subsheets add`, never in the user's data tab, and
  delete that tab afterwards with `sheet subsheets delete`.

## Evidence

- An API `errcode` 0 or a `paste` returning `ok: true` means the request was taken, not
  that the data is right; only `verify` proves content.
- The API read-back shows a dropdown cell's selected value, not the column's option
  list or colors; judge a dropdown's configuration from `dialog-readback`.
- A screenshot is supporting evidence. Dark mode renders fills darker than their stored
  colors, so judge colors from `dialog-readback`, not from pixels.
- The page's data model is undocumented and used here read-only. If a method changes
  and a helper fails, report the failure; do not reconstruct results from memory.

## Resources

- `scripts/cli_grid.py`: `range`, `request`, and `verify` (with `--readback`, and
  `--blank` before writing) for the `wecom-cli` data path.
- `scripts/sheet_js.py` prints one function per subcommand for the browser tool to
  evaluate: `state`, `cf-matches` (with `--range`, `--sheet`, `--expect`), `menu-pick`
  (`--item dropdown|existing-validation|freeze-first-row|new-conditional-format|manage-conditional-formats`
  or `--labels`), `dropdown-colors` (`--map` of option text to a hue such as `red` or
  `red/strong`), `dialog-readback`, and the fallback write path `paste` and `verify`.
- [references/access-paths.md](references/access-paths.md): what `wecom-cli` and the
  import do and do not carry, the official API limits with sources, the browser launch
  the login model relies on, and why a persistent profile or an exported cookie is not
  used.
- [references/ui-recipes.md](references/ui-recipes.md): labels, click paths, dialogs,
  palette values, the browser write path, and known pitfalls of the sheet editor.
