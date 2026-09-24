#!/usr/bin/env python3
"""Generate in-page JavaScript for editing and verifying a WeCom Docs online spreadsheet.

Every subcommand prints one JavaScript function expression. Pass that text unchanged
to the browser tool's "evaluate a function in the page" capability and read the JSON
it returns. Data and UI labels are embedded as UTF-8 JSON literals: escaping every CJK
character as \\u would triple the size of a block that has to travel inside a tool call.

Subcommands:
  paste            write a block of rows via a synthetic paste, refusing unless the Name Box
                   shows the expected anchor and the active tab is the expected sheet
  verify           compare a written block, its links, and its borders against the source,
                   on the expected sheet tab; with --blank, prove the footprint is empty
                   before writing
  cf-matches       count the cells in a range that a conditional format actually colors
  state            report login page, sheet name, size, frozen panes, and filter range
  menu-pick        hover through an open toolbar menu and click the final item
  dropdown-colors  set option colors inside an open data-validation dialog
  dialog-readback  read range, options, and colors of an open data-validation dialog
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

LABELS = {
    "login_title": "\u4f01\u4e1a\u8eab\u4efd\u767b\u5f55",
    "cancel": "\u53d6\u6d88",
    "option_placeholder": "\u8bf7\u8f93\u5165\u9009\u9879",
    "range_placeholder": "\u8bf7\u8f93\u5165\u4e00\u4e2a\u5355\u5143\u683c\u8303\u56f4",
}

MENU_PATHS = {
    "dropdown": ["\u6570\u636e\u9a8c\u8bc1", "\u4e0b\u62c9\u9009\u9879"],
    "existing-validation": ["\u6570\u636e\u9a8c\u8bc1"],
    "freeze-first-row": ["\u51bb\u7ed3\u9996\u884c"],
    "new-conditional-format": ["\u65b0\u5efa\u6761\u4ef6\u683c\u5f0f"],
    "manage-conditional-formats": ["\u7ba1\u7406\u6761\u4ef6\u683c\u5f0f"],
}

HUES = ["gray", "blue", "cyan", "green", "red", "orange", "yellow", "purple", "pink"]
PALETTE = {
    "light": [
        (255, 255, 255), (214, 229, 255), (214, 241, 255), (211, 243, 226), (255, 220, 219),
        (255, 236, 219), (255, 245, 204), (251, 219, 255), (255, 219, 234),
    ],
    "medium": [
        (220, 223, 228), (173, 203, 255), (173, 228, 255), (172, 226, 197), (255, 181, 179),
        (255, 206, 163), (255, 234, 153), (231, 180, 255), (255, 179, 220),
    ],
    "strong": [
        (129, 134, 143), (41, 114, 244), (0, 163, 245), (69, 176, 118), (222, 60, 54),
        (248, 136, 37), (245, 196, 0), (154, 56, 215), (221, 64, 151),
    ],
}

JS_A1 = (
    "const A1 = (r, c) => { let s = \"\"; for (let n = c + 1; n > 0; n = Math.floor((n - 1) / 26))"
    " s = String.fromCharCode(65 + (n - 1) % 26) + s; return s + (r + 1); };"
)

JS_MODEL = (
    "const app = window.SpreadsheetApp;"
    " const sheet = app && app.workbook && app.workbook.activeSheet;"
)

JS_TEXT = (
    "const text = (r, c) => { const d = sheet.getCellDataAtPosition(r, c); if (!d) return \"\";"
    " const f = d.formattedValue; if (f && f.value != null) return String(f.value);"
    " return typeof d.value === \"string\" ? d.value : \"\"; };"
)

JS_POINTER = (
    "const fire = (el, types, atCenter) => { const r = el.getBoundingClientRect();"
    " const o = { bubbles: true, cancelable: true, button: 0,"
    " clientX: r.x + (atCenter ? r.width / 2 : Math.min(10, r.width / 2)), clientY: r.y + r.height / 2 };"
    " types.forEach(t => el.dispatchEvent(new (t.startsWith(\"pointer\") ? PointerEvent : MouseEvent)(t, o))); };"
    " const hover = el => fire(el, [\"pointerover\", \"pointerenter\", \"mouseover\", \"mouseenter\", \"mousemove\"], false);"
    " const click = el => fire(el, [\"pointerdown\", \"mousedown\", \"pointerup\", \"mouseup\", \"click\"], true);"
    " const visible = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.x >= 0; };"
    " const sleep = ms => new Promise(res => setTimeout(res, ms));"
)


class InputError(ValueError):
    pass


def js(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_cell(ref: str) -> tuple[int, int]:
    match = re.fullmatch(r"\$?([A-Za-z]{1,3})\$?([1-9][0-9]*)", ref.strip())
    if not match:
        raise InputError(f"not an A1 cell reference: {ref!r}")
    col = 0
    for ch in match.group(1).upper():
        col = col * 26 + (ord(ch) - 64)
    return int(match.group(2)) - 1, col - 1


def to_a1(row: int, col: int) -> str:
    letters = ""
    n = col + 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return f"{letters}{row + 1}"


def parse_range(ref: str) -> tuple[int, int, int, int]:
    parts = ref.split(":")
    if len(parts) == 1:
        r, c = parse_cell(parts[0])
        return r, c, r, c
    if len(parts) != 2:
        raise InputError(f"not an A1 range: {ref!r}")
    r0, c0 = parse_cell(parts[0])
    r1, c1 = parse_cell(parts[1])
    return min(r0, r1), min(c0, c1), max(r0, r1), max(c0, c1)


def sanitize(value) -> tuple[str, bool]:
    text = "" if value is None else str(value)
    clean = re.sub(r"\r\n|[\r\n\t]", " ", text)
    return clean, clean != text


def load_block(path: Path) -> tuple[list[list[str]], list[list], int]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            raw_rows, links = list(csv.reader(handle)), []
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            raw_rows, links = payload, []
        elif isinstance(payload, dict) and isinstance(payload.get("rows"), list):
            raw_rows, links = payload["rows"], payload.get("links") or []
        else:
            raise InputError("JSON input must be a list of rows or an object with a 'rows' list")
    if not raw_rows or not all(isinstance(row, list) for row in raw_rows):
        raise InputError("input must contain at least one row, and every row must be a list")
    width = max(len(row) for row in raw_rows)
    rows, changed = [], 0
    for row in raw_rows:
        cells = []
        for value in list(row) + [""] * (width - len(row)):
            clean, was_changed = sanitize(value)
            cells.append(clean)
            changed += was_changed
        rows.append(cells)
    for link in links:
        if not (isinstance(link, list) and len(link) == 3 and isinstance(link[0], int) and isinstance(link[1], int)):
            raise InputError(f"each link must be [row, col, url] with zero-based ints: {link!r}")
        if not (0 <= link[0] < len(rows) and 0 <= link[1] < width):
            raise InputError(f"link points outside the block: {link!r}")
        if not re.match(r"https?://", str(link[2])):
            raise InputError(f"link url must be http(s): {link!r}")
    return rows, [[l[0], l[1], str(l[2])] for l in links], changed


def check_sheet_name(sheet_name: str) -> str:
    name = sheet_name.strip()
    if not name:
        raise InputError("--sheet must name the sheet tab, as `state` reports it")
    return name


JS_SHEET_CHECK = (
    " const tab = sheet ? String(sheet.getSheetName()).trim() : null;"
    " const onSheet = tab === expectedSheet;"
)


def build_paste(rows: list[list[str]], links: list[list], anchor: str, sheet_name: str) -> str:
    anchor = to_a1(*parse_cell(anchor))
    expected_sheet = check_sheet_name(sheet_name)
    return (
        "() => { const rows = " + js(rows) + "; const links = " + js(links) + "; const anchor = " + js(anchor) + ";"
        " const expectedSheet = " + js(expected_sheet) + "; " + JS_MODEL + JS_SHEET_CHECK +
        " if (sheet && !onSheet) return { ok: false, error: \"active tab is \" + tab + \", expected \" + expectedSheet"
        " + \"; switch to the expected tab and run paste again\" };"
        " const nameBox = document.querySelector(\"input.bar-label\");"
        " const current = () => nameBox ? nameBox.value.trim().toUpperCase().replace(/\\$/g, \"\") : null;"
        " if (current() !== anchor) return { ok: false, error: \"selection is \" + current() + \", expected \" + anchor"
        " + \"; select the anchor through the Name Box and run paste again\" };"
        " const target = document.getElementById(\"alloy-rich-text-editor\");"
        " if (!target || !target.isContentEditable) return { ok: false, error: \"grid editor not found; the page layout may have changed\" };"
        " if (document.activeElement !== target) target.focus();"
        " if (current() !== anchor) return { ok: false, error: \"focusing the grid moved the selection to \" + current() };"
        " const esc = s => String(s).replace(/&/g, \"&amp;\").replace(/</g, \"&lt;\").replace(/>/g, \"&gt;\").replace(/\"/g, \"&quot;\");"
        " const linkAt = {}; links.forEach(([r, c, u]) => { linkAt[r + \",\" + c] = u; });"
        " const tsv = rows.map(r => r.join(\"\\t\")).join(\"\\n\");"
        " let html = \"<meta charset=\\\"utf-8\\\"><table>\";"
        " rows.forEach((r, i) => { html += \"<tr>\" + r.map((v, j) => { const u = linkAt[i + \",\" + j];"
        " return \"<td>\" + (u ? \"<a href=\\\"\" + esc(u) + \"\\\">\" + esc(v) + \"</a>\" : esc(v)) + \"</td>\"; }).join(\"\") + \"</tr>\"; });"
        " html += \"</table>\";"
        " const dt = new DataTransfer(); dt.setData(\"text/plain\", tsv); dt.setData(\"text/html\", html);"
        " const handled = !target.dispatchEvent(new ClipboardEvent(\"paste\", { clipboardData: dt, bubbles: true, cancelable: true }));"
        " return { ok: handled, anchor, sheet: tab, sheetChecked: !!sheet, rows: rows.length, cols: rows[0].length, links: links.length,"
        " note: !handled ? \"editor ignored the paste\" : sheet ? \"editor accepted the paste; run verify next\""
        " : \"editor accepted the paste, but the active tab could not be read; confirm it from a screenshot\" }; }"
    )


def build_verify(rows: list[list[str]], links: list[list], anchor: str, sheet_name: str) -> str:
    r0, c0 = parse_cell(anchor)
    expected_sheet = check_sheet_name(sheet_name)
    return (
        "() => { " + JS_MODEL + " " + JS_A1 +
        " if (!sheet) return { ok: false, error: \"spreadsheet model not available; verify from screenshots"
        " and report the evidence as weaker\" };"
        " const expectedSheet = " + js(expected_sheet) + ";" + JS_SHEET_CHECK +
        " if (!onSheet) return { ok: false, error: \"active tab is \" + tab + \", expected \" + expectedSheet"
        " + \"; the cells read would belong to the wrong tab\" }; " + JS_TEXT +
        " const rows = " + js(rows) + "; const links = " + js(links) + ";"
        " const r0 = " + js(r0) + "; const c0 = " + js(c0) + "; const width = rows[0].length;"
        " const diffs = []; let checked = 0;"
        " rows.forEach((row, i) => row.forEach((want, j) => { checked += 1; const got = text(r0 + i, c0 + j);"
        " if (got !== want) diffs.push({ cell: A1(r0 + i, c0 + j), want, got }); }));"
        " const linkBad = [];"
        " links.forEach(([r, c, u]) => { const d = sheet.getCellDataAtPosition(r0 + r, c0 + c); let blob = \"\";"
        " try { blob += JSON.stringify(d && d.getHyperlinks ? d.getHyperlinks() : null); } catch (e) {}"
        " try { blob += JSON.stringify(d ? d.value : null); } catch (e) {}"
        " if (!blob.includes(u)) linkBad.push({ cell: A1(r0 + r, c0 + c), want: u }); });"
        " const spill = [];"
        " for (let j = 0; j <= width; j++) { const v = text(r0 + rows.length, c0 + j); if (v !== \"\") spill.push({ cell: A1(r0 + rows.length, c0 + j), got: v }); }"
        " for (let i = 0; i < rows.length; i++) { const v = text(r0 + i, c0 + width); if (v !== \"\") spill.push({ cell: A1(r0 + i, c0 + width), got: v }); }"
        " return { ok: diffs.length === 0 && linkBad.length === 0 && spill.length === 0,"
        " sheet: sheet.getSheetName(), range: A1(r0, c0) + \":\" + A1(r0 + rows.length - 1, c0 + width - 1),"
        " checked, diffCount: diffs.length, diffs: diffs.slice(0, 20), linksChecked: links.length,"
        " linkBad: linkBad.slice(0, 20), spill: spill.slice(0, 20) }; }"
    )


def build_cf_matches(cell_range: str, sheet_name: str, expect: int | None) -> str:
    r0, c0, r1, c1 = parse_range(cell_range)
    expected_sheet = check_sheet_name(sheet_name)
    return (
        "() => { " + JS_MODEL + " " + JS_A1 +
        " if (!sheet) return { ok: false, error: \"spreadsheet model not available; conditional-format matches"
        " cannot be read\" };"
        " const expectedSheet = " + js(expected_sheet) + ";" + JS_SHEET_CHECK +
        " if (!onSheet) return { ok: false, error: \"active tab is \" + tab + \", expected \" + expectedSheet };"
        " " + JS_TEXT +
        " const r0 = " + js(r0) + "; const c0 = " + js(c0) + "; const r1 = " + js(r1) + "; const c1 = " + js(c1) + ";"
        " const expect = " + js(expect) + ";"
        " const matched = []; const unmatched = {}; let checked = 0; let unreadable = 0;"
        " for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) { checked += 1;"
        " const d = sheet.getCellDataAtPosition(r, c); let res;"
        " try { res = d && d.getConditionalFormattingResult ? d.getConditionalFormattingResult() : null; }"
        " catch (e) { unreadable += 1; continue; }"
        " let raw = \"null\"; try { raw = JSON.stringify(res) || \"null\"; } catch (e) { raw = String(res); }"
        " if (res != null && raw !== \"{}\" && raw !== \"[]\" && raw !== \"null\")"
        " matched.push({ cell: A1(r, c), value: text(r, c), result: raw.slice(0, 200) });"
        " else { const v = text(r, c); unmatched[v] = (unmatched[v] || 0) + 1; } }"
        " const countOk = expect === null || matched.length === expect;"
        " return { ok: unreadable === 0 && countOk, sheet: tab, range: A1(r0, c0) + \":\" + A1(r1, c1), checked,"
        " matchedCount: matched.length, expected: expect, matched: matched.slice(0, 20),"
        " unmatchedValues: Object.entries(unmatched).slice(0, 20), unreadable }; }"
    )


def build_state() -> str:
    return (
        "() => { " + JS_MODEL + " " + JS_A1 +
        " const loginPage = Array.from(document.querySelectorAll(\"body *\")).some(e => e.children.length === 0"
        " && (e.innerText || \"\").trim() === " + js(LABELS["login_title"]) + ");"
        " if (!sheet) return { ok: false, title: document.title, loginPage, modelAvailable: false };"
        " let filter = null;"
        " try { const fm = sheet.getFilterManager && sheet.getFilterManager(); const r = fm && fm.getFilterRange();"
        " if (r) filter = A1(r.startRowIndex, r.startColIndex) + \":\" + A1(r.endRowIndex, r.endColIndex); }"
        " catch (e) { filter = \"unreadable\"; }"
        " return { ok: true, title: document.title, loginPage, modelAvailable: true, sheet: sheet.getSheetName(),"
        " rowCount: sheet.getRowCount(), colCount: sheet.getColCount(), frozenRows: sheet.getFrozenRowCount(),"
        " frozenCols: sheet.getFrozenColCount(), filter }; }"
    )


def build_menu_pick(labels: list[str]) -> str:
    return (
        "async () => { " + JS_POINTER + " const labels = " + js(labels) + ";"
        " const norm = el => (el.innerText || \"\").trim().replace(/\\s+/g, \" \");"
        " const find = label => Array.from(document.querySelectorAll(\"li, [role=menuitem]\")).find(el => visible(el) && norm(el).startsWith(label));"
        " const trail = [];"
        " for (let i = 0; i < labels.length; i++) { let el = null;"
        " for (let k = 0; k < 10 && !el; k++) { el = find(labels[i]); if (!el) await sleep(100); }"
        " if (!el) return { ok: false, missing: labels[i], trail,"
        " visibleItems: Array.from(document.querySelectorAll(\"li\")).filter(visible).map(norm).slice(0, 30) };"
        " trail.push(norm(el)); if (i < labels.length - 1) { hover(el); await sleep(300); } else { click(el); await sleep(300); } }"
        " return { ok: true, trail }; }"
    )


def resolve_color(spec: str, default_shade: str) -> tuple[int, int, int]:
    hue, _, shade = spec.strip().lower().partition("/")
    shade = shade or default_shade
    if shade not in PALETTE:
        raise InputError(f"unknown shade {shade!r}; use one of {sorted(PALETTE)}")
    if hue == "white":
        if shade != "light":
            raise InputError("white exists only as white/light")
        return PALETTE["light"][0]
    if hue == "gray" and shade == "light":
        raise InputError("the light row has white instead of gray; use gray/medium or white/light")
    if hue not in HUES:
        raise InputError(f"unknown color {hue!r}; use one of {HUES + ['white']}")
    return PALETTE[shade][HUES.index(hue)]


def build_dropdown_colors(mapping: dict[str, str], default_shade: str) -> str:
    wanted = [[option, "rgb({}, {}, {})".format(*resolve_color(spec, default_shade))] for option, spec in mapping.items()]
    return (
        "async () => { " + JS_POINTER + " const wanted = " + js(wanted) + ";"
        " const inputs = () => Array.from(document.querySelectorAll(\"input[placeholder=\" + JSON.stringify(" + js(LABELS["option_placeholder"]) + ") + \"]\"));"
        " if (!inputs().length) return { ok: false, error: \"no data validation dialog with options is open\" };"
        " const palette = () => Array.from(document.querySelectorAll(\".dui-colorpicker-item\")).filter(visible);"
        " const results = [];"
        " for (const [option, rgb] of wanted) { const input = inputs().find(i => i.value === option);"
        " const box = input && input.closest(\".input-container\"); const block = box && box.querySelector(\".color-block\");"
        " if (!block) { results.push({ option, want: rgb, got: null, error: \"option not in dialog\" }); continue; }"
        " if (!palette().length) { click(block); await sleep(350); }"
        " const swatch = palette().find(e => getComputedStyle(e).backgroundColor === rgb);"
        " if (!swatch) { results.push({ option, want: rgb, got: getComputedStyle(block).backgroundColor, error: \"color not in palette\" }); continue; }"
        " click(swatch); await sleep(350); results.push({ option, want: rgb, got: getComputedStyle(block).backgroundColor }); }"
        " const unmapped = inputs().map(i => i.value).filter(v => !wanted.some(([o]) => o === v));"
        " return { ok: results.every(r => r.got === r.want), results, unmapped }; }"
    )


def build_dialog_readback(keep_open: bool) -> str:
    return (
        "async () => { const range = document.querySelector(\"input[placeholder=\" + JSON.stringify("
        + js(LABELS["range_placeholder"]) + ") + \"]\");"
        " if (!range) return { ok: false, error: \"no data validation dialog is open\" };"
        " const options = Array.from(document.querySelectorAll(\"input[placeholder=\" + JSON.stringify("
        + js(LABELS["option_placeholder"]) + ") + \"]\")).map(i => { const box = i.closest(\".input-container\");"
        " const block = box && box.querySelector(\".color-block\");"
        " return { text: i.value, color: block ? getComputedStyle(block).backgroundColor : null }; });"
        " const result = { ok: true, range: range.value, options };"
        " if (!" + js(keep_open) + ") { const cancel = Array.from(document.querySelectorAll(\"button\")).find(b =>"
        " (b.innerText || \"\").trim() === " + js(LABELS["cancel"]) + " && b.getBoundingClientRect().width > 0);"
        " if (cancel) cancel.click(); result.cancelled = !!cancel; }"
        " return result; }"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_paste = sub.add_parser("paste", help="write rows at the selected anchor cell")
    p_paste.add_argument("--input", required=True, type=Path, help="CSV, JSON rows, or {rows, links} JSON")
    p_paste.add_argument("--anchor", required=True, help="cell the Name Box must show before pasting, e.g. A1")
    p_paste.add_argument("--sheet", required=True, help="sheet tab the block belongs on, as `state` reports it")

    p_verify = sub.add_parser("verify", help="compare the written block with the source")
    p_verify.add_argument("--input", required=True, type=Path)
    p_verify.add_argument("--anchor", required=True, help="top-left cell of the block, e.g. A1")
    p_verify.add_argument("--sheet", required=True, help="sheet tab the block belongs on, as `state` reports it")
    p_verify.add_argument(
        "--blank",
        action="store_true",
        help="expect every cell of the block's footprint to be empty; run before writing",
    )

    p_cf = sub.add_parser("cf-matches", help="count cells a conditional format actually colors")
    p_cf.add_argument("--range", required=True, help="the rule's apply range, e.g. K2:K77")
    p_cf.add_argument("--sheet", required=True, help="sheet tab the rule belongs to, as `state` reports it")
    p_cf.add_argument(
        "--expect",
        type=int,
        help="number of cells the rule should color, counted from the source data; ok requires it",
    )

    sub.add_parser("state", help="report login, sheet, frozen panes, and filter")

    p_menu = sub.add_parser("menu-pick", help="click through an open toolbar menu")
    group = p_menu.add_mutually_exclusive_group(required=True)
    group.add_argument("--item", choices=sorted(MENU_PATHS))
    group.add_argument("--labels", nargs="+", help="visible menu labels, outermost first")

    p_colors = sub.add_parser("dropdown-colors", help="color options in an open data-validation dialog")
    p_colors.add_argument("--map", required=True, help="JSON object: option text -> color or color/shade")
    p_colors.add_argument("--shade", default="medium", choices=sorted(PALETTE))

    p_read = sub.add_parser("dialog-readback", help="read an open data-validation dialog, then cancel it")
    p_read.add_argument("--keep-open", action="store_true", help="read without cancelling")

    args = parser.parse_args(argv)
    try:
        if args.command == "paste":
            rows, links, changed = load_block(args.input)
            if changed:
                print(f"note: {changed} cell(s) had tabs or line breaks replaced by spaces", file=sys.stderr)
            print(build_paste(rows, links, args.anchor, args.sheet))
        elif args.command == "verify":
            rows, links, _ = load_block(args.input)
            if args.blank:
                rows, links = [[""] * len(rows[0]) for _ in rows], []
            print(build_verify(rows, links, args.anchor, args.sheet))
        elif args.command == "cf-matches":
            if args.expect is not None and args.expect < 0:
                raise InputError("--expect must be zero or more")
            print(build_cf_matches(args.range, args.sheet, args.expect))
        elif args.command == "state":
            print(build_state())
        elif args.command == "menu-pick":
            print(build_menu_pick(MENU_PATHS[args.item] if args.item else args.labels))
        elif args.command == "dropdown-colors":
            mapping = json.loads(args.map)
            if not isinstance(mapping, dict) or not mapping:
                raise InputError("--map must be a non-empty JSON object")
            print(build_dropdown_colors(mapping, args.shade))
        elif args.command == "dialog-readback":
            print(build_dialog_readback(args.keep_open))
    except (InputError, json.JSONDecodeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
