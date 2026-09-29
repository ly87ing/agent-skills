# Sheet editor recipes

Table of Contents

1. Labels
2. Selecting a range
3. Writing and reading cells
4. Colored dropdown options
5. Palette
6. Conditional formatting
7. Filter and frozen rows
8. Clicking menus that are not in the accessibility tree
9. Pitfalls observed in practice

The editor's labels are Chinese. They are written below as `\u` escapes; decode them
when matching page text, and prefer `scripts/sheet_js.py`, which already embeds them.
Everything here was observed on the live editor on 2026-09-23 unless dated otherwise;
re-check a recipe the first time it fails rather than assuming the page is broken.

## 1. Labels

| Meaning | Label |
| --- | --- |
| Enterprise login page title | `\u4f01\u4e1a\u8eab\u4efd\u767b\u5f55` |
| Toolbar: Data | `\u6570\u636e` |
| Data validation (submenu) | `\u6570\u636e\u9a8c\u8bc1` |
| Dropdown options | `\u4e0b\u62c9\u9009\u9879` |
| Toolbar: Conditional format | `\u6761\u4ef6\u683c\u5f0f` |
| New conditional format | `\u65b0\u5efa\u6761\u4ef6\u683c\u5f0f` |
| Manage conditional formats | `\u7ba1\u7406\u6761\u4ef6\u683c\u5f0f` |
| Current sheet (tab in the manage panel) | `\u5f53\u524d\u5de5\u4f5c\u8868` |
| Delete all | `\u5168\u90e8\u5220\u9664` |
| Toolbar: Filter | `\u7b5b\u9009` |
| Toolbar: Freeze | `\u51bb\u7ed3` |
| Freeze first row | `\u51bb\u7ed3\u9996\u884c` |
| Cancel / Confirm | `\u53d6\u6d88` / `\u786e\u5b9a` |
| Multi-select / Color (dropdown dialog checkboxes) | `\u591a\u9009` / `\u989c\u8272` |
| Manual entry / Reference data (dropdown option source) | `\u624b\u52a8\u8f93\u5165` / `\u5f15\u7528\u6570\u636e` |
| File operations (title bar) / Delete document / Confirm delete | `\u6309\u94ae:\u6587\u4ef6\u64cd\u4f5c` / `\u5220\u9664\u6587\u6863` / `\u786e\u5b9a\u5220\u9664` |

## 2. Selecting a range

The Name Box is the text box left of the formula bar (an input with class `bar-label`
when observed); its value is the active cell, the top-left cell of a selected range.
Fill it with `A1`, `G2:J77`, or any range and press Enter. The status bar then shows
the count of non-empty cells in the selection, a quick cross-check of the selection
size. Clicking cells by screen position is fragile; use the Name Box.

Read the Name Box again before acting on a selection. After a Name Box selection
followed by toolbar and menu clicks, a dialog once opened on the cell one row below the
one typed; `paste` therefore refuses to write unless the Name Box shows its anchor.
After Enter, focus leaves the Name Box for the page, not the grid.

## 3. Writing and reading cells

This is the fallback write path for when `wecom-cli` is unavailable; the default data
path is in SKILL.md. Before writing, evaluate `verify --input BLOCK --anchor A1 --sheet
TAB --blank` and require `ok: true`. Then select the anchor through the Name Box and
evaluate `paste --input BLOCK --anchor A1 --sheet TAB`: it refuses unless the active tab
is TAB and the Name Box shows exactly that anchor, then focuses the grid and pastes as
one undoable user action that syncs like typing. If it returns `sheetChecked: false`,
confirm the tab from a screenshot. Finish with `verify` on the same file, anchor, and
tab. Never write through the page's internal data model.

- The grid's input proxy is a content-editable element (id `alloy-rich-text-editor`
  when observed). Focusing it with a script keeps the selection where it is. `paste`
  focuses it, then dispatches a synthetic paste event carrying tab-separated text and an
  HTML table; the editor spreads the block from the selected cell. Cells linked through
  an `<a href>` in the HTML become rich-text links.
- Reading goes through `window.SpreadsheetApp.workbook.activeSheet`:
  `getCellDataAtPosition(row, col)` with zero-based indexes, `.formattedValue.value` for
  the displayed text, `getHyperlinks()` and `.value` for link payloads,
  `getFilterManager().getFilterRange()` for the filter range (inclusive indexes), and
  `getFrozenRowCount()` / `getFrozenColCount()`.
- A synthetic copy event does not fill its clipboard data, so copying the selection is
  not a way to read cells back.

## 4. Colored dropdown options

1. Select the target range through the Name Box.
2. Click the toolbar button Data, then run `menu-pick --item dropdown`. On a range that
   already has validation, the submenu item reads "Data validation" followed by its
   type; `menu-pick --item existing-validation` opens the stored configuration.
3. The "set data validation" dialog pre-fills the range and one option per distinct
   value already in the range. Check that list against the intended vocabulary: a typo
   in the data becomes an option.
4. Keep the Color checkbox on and Multi-select off unless asked. Run `dropdown-colors
   --map '{"<option>": "red", ...}'`; it opens each option's swatch and picks the
   palette color, returning wanted and actual colors per option plus any options the
   map did not cover.
5. Click Confirm (accessible button in the dialog). A toast confirms the save.
6. Read back: select a corner cell, reopen with `existing-validation`, run
   `dialog-readback`, and repeat on a cell just outside the range, which must show no
   type after "Data validation".

## 5. Palette

Nine hues in three shades. The first slot of the light row is white; gray exists only
in the medium and strong rows. `dropdown-colors` defaults to medium, which stays
readable as a chip in both light and dark themes.

| Hue | light | medium | strong |
| --- | --- | --- | --- |
| gray (white in light) | 255, 255, 255 | 220, 223, 228 | 129, 134, 143 |
| blue | 214, 229, 255 | 173, 203, 255 | 41, 114, 244 |
| cyan | 214, 241, 255 | 173, 228, 255 | 0, 163, 245 |
| green | 211, 243, 226 | 172, 226, 197 | 69, 176, 118 |
| red | 255, 220, 219 | 255, 181, 179 | 222, 60, 54 |
| orange | 255, 236, 219 | 255, 206, 163 | 248, 136, 37 |
| yellow | 255, 245, 204 | 255, 234, 153 | 245, 196, 0 |
| purple | 251, 219, 255 | 231, 180, 255 | 154, 56, 215 |
| pink | 255, 219, 234 | 255, 179, 220 | 221, 64, 151 |

## 6. Conditional formatting

- Toolbar Conditional format opens a menu whose items are not in the accessibility
  tree; use `menu-pick --item new-conditional-format` or
  `--item manage-conditional-formats`.
- The new-rule sidebar is accessible: an "apply range" text box pre-filled with the
  selection, a style-type combobox (highlight cells, top/bottom, custom formula, color
  scale, data bar, icon set), a rule-category combobox (number, content, date,
  duplicate, unique), an operator combobox (content: contains, does not contain, equals,
  empty, not empty, starts with, ends with, ...), a value box, and a display preset
  (light red fill with dark red text, light yellow, light green, gray, red text,
  strikethrough, custom). Creating a rule switches the sidebar to the rule list.
- Use "equals" rather than "contains" for fixed values, so a longer value that merely
  contains the word is not colored by accident.
- A custom formula is relative to the top-left cell of the apply range, for example
  `=OR(LEFT(K2,1)="A",LEFT(K2,1)="B")` for `K2:K77`.
- The rule list opens on "selected range"; switch to the current-sheet tab to see every
  rule before deleting anything. "Delete all" asks for confirmation with the number of
  rules; compare it with the rules this session created.
- Per-cell results can be read with `getConditionalFormattingResult()` on a cell from
  the data model, whose fill color names the rule that matched. `cf-matches` counts a
  cell as colored when that result is non-empty, and lists the matched cells and the
  values it left uncolored. That empty-versus-filled reading was not re-checked on the
  live editor when the helper was added, so on its first run compare one cell that
  should match and one that should not before trusting the count.

## 7. Filter and frozen rows

- Select the header-plus-data range through the Name Box and click the toolbar Filter
  button; each header cell gets a filter control. `state` reports the filter range.
- Toolbar Freeze opens a menu; `menu-pick --item freeze-first-row`. `state` reports
  `frozenRows`.
- The data model exposes a local-filter flag whose value was observed to flip between
  reads of the same sheet. It does not tell whether collaborators see a filter; do not
  report that from it.

## 8. Clicking menus that are not in the accessibility tree

Toolbar buttons and sidebar controls are accessible and can be clicked with the browser
tool directly. Their drop-down menus are plain list items: a submenu opens on hover and
an item acts on a full pointer sequence (pointerdown, mousedown, pointerup, mouseup,
click) at its center. `menu-pick` performs both and waits between steps. Open the
toolbar menu first with the browser tool, then run `menu-pick`.

## 9. Pitfalls observed in practice

- A tab or line break inside a value shifts every later column of a paste; the
  generator replaces them with spaces and reports how many cells it changed.
- Dark mode draws fills darker than the stored colors; screenshots misjudge colors.
- The dropdown dialog lists one option per distinct value found in the range, so data
  errors surface there first.
- With the automation window minimized, the page still reported `visibilityState`
  "visible" and `hasFocus()` true; only the operating system's window state showed it
  minimized. Everything in this file kept working in that state.
- A menu or dialog can act on a different cell than the one typed into the Name Box;
  check the Name Box, and read the range field of any dialog before confirming it.
- Observed on 2026-09-29: at a 1200 px wide window the toolbar folded, and its Data
  button opened a menu whose Data validation item sat one submenu deeper, so
  `menu-pick --item dropdown` reported it missing. At 1680 px the documented paths
  worked again; set the window width before driving menus.
- A dropdown imported from an `.xlsx` list validation uses the reference-data source
  (the option list sits in one text box, for example `a,b,c`) and has no color
  swatches. The first `dialog-readback` read only manual-entry inputs and returned a
  hidden leftover as an option; it now reports `source: "reference"` with the box's
  list, built from that day's page snapshot and checked only against a stand-in page,
  so compare it once with a screenshot on first live use. Recoloring an
  imported dropdown was not tried: if `dropdown-colors` finds no swatches, remove that
  validation (only when this session created it) and add a manual-entry dropdown as in
  section 4.
- `wecom-cli` has no command to delete a document. In the page, the title-bar file
  operations button opens a menu with Delete document, and its confirmation says the
  document goes to the user's recycle bin; delete only documents this session created.
- The browser tool transports UTF-8 function text; escaping every CJK character as
  `\u` roughly triples a data block, so the generator keeps data as UTF-8.
