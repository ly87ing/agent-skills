---
name: wecom-docs-editing
description: "Writes, formats, and verifies WeCom Docs online spreadsheets (doc.weixin.qq.com/sheet) in a logged-in browser: pastes row blocks, reads every cell back, sets colored dropdowns, conditional formats, filters, and frozen rows. Use when the target is a live WeCom sheet that other people share."
---

# WeCom Docs Editing

Put data and formatting into a WeCom Docs online spreadsheet that other people read,
and prove every cell landed where it should. A shared sheet is read by people who never
see this session, so a column shifted by one stray tab, or a rule that silently matched
nothing, does more damage than a write that visibly failed. Treat the page's own
"accepted" signals as hints and a cell-by-cell read-back as the only proof.

Scope is the spreadsheet editor at `doc.weixin.qq.com/sheet/...`. Documents
(`/doc/`) and smart sheets (`/smartsheet/`) run different editors; for those, say the
skill does not cover them yet and stop instead of improvising selectors.

## Choose the access path

- The official WeCom document API can only read and edit documents that the calling
  app created, and its spreadsheet update covers cell content and sheet/row structure
  only - no dropdowns, conditional formats, filters, or frozen panes. Use it only when
  the team already owns an app-created sheet and a content-only change; the details and
  sources are in [references/access-paths.md](references/access-paths.md).
- Everything else, including every member-created sheet, goes through a browser
  session logged in as the user.

## Session and credentials

The login lasts one work session: the user logs in once, the work reuses it, and it is
discarded when the browser closes.

- Drive a browser automation instance that starts on a temporary profile (an isolated
  mode), so the session cookie lives only as long as that browser. If the only instance
  available keeps a persistent profile, say that the login would stay on disk after the
  work and ask before logging in; the reasons are in
  [references/access-paths.md](references/access-paths.md).
- Open the sheet URL, in a background tab when the tool offers one, then run
  `python3 scripts/sheet_js.py state` and evaluate the printed function in the page. If
  `loginPage` is true, ask the user to finish the enterprise login in that window (quick
  login or QR code) and wait. Do not type a password, and click the login control only
  when the user asks for it.
- After the login the user may minimize the window; the tested behavior and why the
  page's own visibility cannot confirm it are in
  [references/access-paths.md](references/access-paths.md). Keep the browser open
  until the work is done: closing it discards the login, and the next step needs a new
  one.
- Never export, store, print, or inject cookies or tokens. The session cookie is the
  whole account with no scope limit, so it stays in the temporary profile and nowhere
  else.
- If `loginPage` turns true in the middle of the work, the session expired: stop, ask
  for a new login, and resume from step 2 of the workflow.
- If the toolbar is missing or disabled, the account can only view the sheet: stop and
  report that. If `modelAvailable` is false, writing still works but verification drops
  to screenshots; say that the evidence is weaker instead of implying a full check.

## Workflow

1. **Lock the target.** Record the sheet URL, document title, sheet tab (the `sheet`
   name `state` reports; pass it as `--sheet TAB` to every command below), anchor cell,
   and the source of the rows. Put the block in a JSON or CSV file in a scratch
   location, not in any repository: a list of rows, or `{"rows": [...], "links":
   [[row, col, url], ...]}` with zero-based positions inside the block.
2. **Look before writing.** Generate `verify --input BLOCK --anchor A1 --sheet TAB --blank`
   and evaluate it. `ok: true` means the footprint and its right and bottom borders are
   empty. When resuming interrupted work, run the full `verify` first: if the block is
   already there exactly, skip to step 4 instead of writing it twice. Anything else is
   someone's data: show the non-empty cells and ask before overwriting.
3. **Write.** Select the anchor by typing it into the Name Box left of the formula bar
   and pressing Enter, then evaluate `paste --input BLOCK --anchor A1 --sheet TAB`. It
   refuses unless the active tab is TAB and the Name Box shows exactly that anchor,
   because the selection can drift (see the pitfalls in ui-recipes); then it focuses
   the grid itself and pastes. If it returns `sheetChecked: false`, the tab could not be
   read: confirm it from a screenshot before going on. One paste
   is one undoable user action that syncs to collaborators like typing does; never
   write through the page's internal data model.
4. **Verify.** Evaluate `verify --input BLOCK --anchor A1 --sheet TAB` with the same
   file, anchor, and tab. Require `ok: true`: the right tab, every cell equal, every link
   present, nothing spilled past the block. Report any diff as found; the sheet may reformat number-like text (leading
   zeros, dates), and whether to keep that is the user's call, not a silent retry.
5. **Format on request.** Prefer colored dropdown options for columns with a fixed
   vocabulary: they color every value and reject typos that would make a text rule miss.
   Use conditional formatting for open text or formula rules, then a filter and a frozen
   header. After each change, read it back through its own surface - `dialog-readback`
   on a corner cell and on a cell just outside the range for dropdowns, `state` for the
   filter and frozen rows. For a conditional format, a rule in the list is not proof it
   works: count from the source data how many cells in the apply range it should color,
   then require `ok: true` from `cf-matches --range K2:K77 --sheet TAB --expect N`. A
   rule that colors fewer or more cells than that is a failed rule to fix, not a
   finished one.
   Click paths, labels, and the palette are in
   [references/ui-recipes.md](references/ui-recipes.md).
6. **Report.** State the tab and range written, cells compared, the diff count, links
   checked, each formatting change with its read-back (for a conditional format, the
   cells it colors against the count expected), and what was not verified.

## Stop and ask

- Before overwriting non-empty cells, deleting or replacing rules and validations that
  this session did not create, or clearing the whole sheet's rules. The delete-all
  confirmation states a rule count; proceed only when it equals what this session made.
- Before a change the user did not ask for that alters what collaborators see, such as
  a filter that hides rows or a sort. A filter the user asked for is added directly.
  Either way, whether a filter is shared with collaborators could not be established
  from the page, so describe that risk in the report instead of asserting either way.
- After adding a dropdown, values outside its list become invalid; say so.
- When a label or element is missing, `menu-pick` returns the visible menu items. Stop
  and report them; do not guess by screen coordinates, because a changed page makes a
  guessed click land on the wrong control.
- Close every dialog opened only for reading: `dialog-readback` cancels by default.

## Evidence

- `paste` returning `ok: true` means the editor took the event, not that the data is
  right; only `verify` proves content.
- A screenshot is supporting evidence. Dark mode renders fills darker than their stored
  colors, so judge colors from `dialog-readback`, not from pixels.
- The page's data model is undocumented and used here read-only. If a method changes
  and a helper fails, report the failure; do not reconstruct results from memory.

## Resources

- `scripts/sheet_js.py` prints one function per subcommand for the browser tool to
  evaluate: `paste` (with `--anchor` and `--sheet`), `verify` (with `--sheet`, and
  `--blank` before writing), `cf-matches` (with `--range`, `--sheet`, `--expect`),
  `state`, `menu-pick`
  (`--item dropdown|existing-validation|freeze-first-row|new-conditional-format|manage-conditional-formats`
  or `--labels`), `dropdown-colors` (`--map` of option text to a hue such as `red` or
  `red/strong`), and `dialog-readback`.
- [references/ui-recipes.md](references/ui-recipes.md): labels, click paths, dialogs,
  palette values, and known pitfalls of the sheet editor.
- [references/access-paths.md](references/access-paths.md): official API limits with
  sources, the browser launch the login model relies on, and why a persistent profile
  or an exported cookie is not used.
