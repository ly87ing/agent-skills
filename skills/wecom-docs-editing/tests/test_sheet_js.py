"""Guard the JavaScript generator that the skill hands to the browser.

The generated functions run inside a live, shared spreadsheet, so the failure modes
worth pinning are the silent ones: a tab or line break inside a cell shifting every
later column of the paste, an anchor parsed one column off so verification compares
the wrong cells and still reports them, a paste and read-back that both land on the
wrong sheet tab and agree with each other, a conditional format that colors nothing, a
CJK label that no longer matches the page, and a color name that resolves to a swatch
the palette does not have.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sheet_js.py"
SPEC = importlib.util.spec_from_file_location("sheet_js", SCRIPT)
sheet_js = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sheet_js)

MISSING = "\u7f3a\u5931"
SHEET = "Sheet1"
PARTIAL = "\u4e0d\u8db3"
WORKDIR = tempfile.TemporaryDirectory()


def tearDownModule():
    WORKDIR.cleanup()


def embedded(source: str, name: str):
    match = re.search(r"const " + name + r" = (.+?);(?= )", source)
    if not match:
        raise AssertionError(f"{name} literal not found")
    return json.loads(match.group(1))


def scratch_file(suffix: str, text: str, encoding: str = "utf-8") -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=suffix, dir=WORKDIR.name, delete=False, encoding=encoding)
    handle.write(text)
    handle.close()
    return Path(handle.name)


def write_json(payload) -> Path:
    return scratch_file(".json", json.dumps(payload, ensure_ascii=False))


class CellReferenceTests(unittest.TestCase):
    def test_parses_cells_zero_based(self):
        self.assertEqual(sheet_js.parse_cell("A1"), (0, 0))
        self.assertEqual(sheet_js.parse_cell("L77"), (76, 11))
        self.assertEqual(sheet_js.parse_cell("$AA$10"), (9, 26))

    def test_round_trips_through_a1(self):
        for row, col in [(0, 0), (76, 11), (9, 25), (9, 26), (0, 701), (0, 702)]:
            self.assertEqual(sheet_js.parse_cell(sheet_js.to_a1(row, col)), (row, col))

    def test_normalises_reversed_ranges(self):
        self.assertEqual(sheet_js.parse_range("L77:A1"), (0, 0, 76, 11))
        self.assertEqual(sheet_js.parse_range("C3"), (2, 2, 2, 2))

    def test_rejects_malformed_references(self):
        for bad in ("A0", "1A", "A1:B2:C3", "", "ABCD1"):
            with self.assertRaises(sheet_js.InputError, msg=bad):
                sheet_js.parse_range(bad)


class BlockLoadingTests(unittest.TestCase):
    def test_replaces_tabs_and_line_breaks_that_would_shift_columns(self):
        path = write_json([["a\tb", "line1\nline2"], ["x\r\ny", None]])
        rows, _, changed = sheet_js.load_block(path)
        self.assertEqual(rows, [["a b", "line1 line2"], ["x y", ""]])
        self.assertEqual(changed, 3)

    def test_pads_ragged_rows_to_a_rectangle(self):
        rows, _, _ = sheet_js.load_block(write_json([["h1", "h2", "h3"], ["only"]]))
        self.assertEqual(rows[1], ["only", "", ""])

    def test_reads_csv_with_bom(self):
        path = scratch_file(".csv", "id,status\n1," + MISSING + "\n", encoding="utf-8-sig")
        rows, links, _ = sheet_js.load_block(path)
        self.assertEqual(rows, [["id", "status"], ["1", MISSING]])
        self.assertEqual(links, [])

    def test_rejects_links_outside_the_block_or_not_http(self):
        with self.assertRaises(sheet_js.InputError):
            sheet_js.load_block(write_json({"rows": [["a"]], "links": [[1, 0, "https://x.test"]]}))
        with self.assertRaises(sheet_js.InputError):
            sheet_js.load_block(write_json({"rows": [["a"]], "links": [[0, 0, "javascript:alert(1)"]]}))


class GeneratedJavaScriptTests(unittest.TestCase):
    def setUp(self):
        self.rows = [["id", "status", "note"], ["625931", MISSING, "a < b & c"], ["626358", PARTIAL, ""]]
        self.links = [[1, 0, "https://example.test/task/abc"]]

    def test_paste_embeds_rows_and_links_verbatim(self):
        source = sheet_js.build_paste(self.rows, self.links, "A1", SHEET)
        self.assertIn(MISSING, source, "CJK data should travel as UTF-8, not tripled by escapes")
        self.assertEqual(embedded(source, "rows"), self.rows)
        self.assertEqual(embedded(source, "links"), self.links)
        self.assertIn("ClipboardEvent", source)

    def test_paste_refuses_unless_the_name_box_shows_the_normalised_anchor(self):
        source = sheet_js.build_paste(self.rows, self.links, "$k$2", SHEET)
        self.assertEqual(embedded(source, "anchor"), "K2")
        self.assertLess(source.index("current() !== anchor"), source.index("dispatchEvent(new ClipboardEvent"))
        with self.assertRaises(sheet_js.InputError):
            sheet_js.build_paste(self.rows, self.links, "K0", SHEET)

    def test_verify_uses_the_anchor_offsets(self):
        source = sheet_js.build_verify(self.rows, self.links, "C5", SHEET)
        self.assertEqual(embedded(source, "r0"), 4)
        self.assertEqual(embedded(source, "c0"), 2)
        self.assertEqual(embedded(source, "rows"), self.rows)

    def test_paste_checks_the_tab_before_touching_the_grid(self):
        source = sheet_js.build_paste(self.rows, self.links, "A1", " Sheet1 ")
        self.assertEqual(embedded(source, "expectedSheet"), SHEET)
        self.assertLess(source.index("!onSheet"), source.index("dispatchEvent(new ClipboardEvent"))
        with self.assertRaises(sheet_js.InputError):
            sheet_js.build_paste(self.rows, self.links, "A1", "  ")

    def test_cf_matches_embeds_the_range_and_expected_count(self):
        source = sheet_js.build_cf_matches("K77:K2", SHEET, 12)
        self.assertEqual(
            [embedded(source, name) for name in ("r0", "c0", "r1", "c1", "expect")], [1, 10, 76, 10, 12]
        )
        self.assertIsNone(embedded(sheet_js.build_cf_matches("K2", SHEET, None), "expect"))

    def test_menu_aliases_expand_to_the_page_labels(self):
        source = sheet_js.build_menu_pick(sheet_js.MENU_PATHS["dropdown"])
        self.assertEqual(embedded(source, "labels"), ["\u6570\u636e\u9a8c\u8bc1", "\u4e0b\u62c9\u9009\u9879"])

    def test_dropdown_colors_resolve_to_palette_rgb(self):
        source = sheet_js.build_dropdown_colors({MISSING: "red", PARTIAL: "yellow/strong"}, "medium")
        self.assertEqual(
            embedded(source, "wanted"),
            [[MISSING, "rgb(255, 181, 179)"], [PARTIAL, "rgb(245, 196, 0)"]],
        )

    def test_every_generated_function_is_valid_javascript(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        sources = {
            "paste": sheet_js.build_paste(self.rows, self.links, "A1", SHEET),
            "verify": sheet_js.build_verify(self.rows, self.links, "A1", SHEET),
            "cf-matches": sheet_js.build_cf_matches("B2:B3", SHEET, 1),
            "state": sheet_js.build_state(),
            "menu-pick": sheet_js.build_menu_pick(["x", "y"]),
            "dropdown-colors": sheet_js.build_dropdown_colors({MISSING: "green"}, "medium"),
            "dialog-readback": sheet_js.build_dialog_readback(False),
        }
        for name, source in sources.items():
            path = scratch_file(".js", "const f = " + source + ";\n")
            result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, f"{name}: {result.stderr}")


FAKE_SHEET = """
const window = { SpreadsheetApp: { workbook: { activeSheet: {
  getSheetName: () => TAB,
  getCellDataAtPosition: (r, c) => {
    const v = (CELLS[r] || [])[c];
    if (v === undefined) return null;
    return { value: v, formattedValue: { value: v },
      getConditionalFormattingResult: () => (RULED.includes(v) ? { fill: "rgb(255, 220, 219)" } : null) };
  },
} } } };
"""


def run_in_fake_sheet(source: str, tab: str, cells: list[list[str]], ruled: list[str]) -> dict:
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    script = (
        f"const TAB = {json.dumps(tab)}; const CELLS = {json.dumps(cells, ensure_ascii=False)};"
        f" const RULED = {json.dumps(ruled, ensure_ascii=False)};"
        + FAKE_SHEET
        + "console.log(JSON.stringify((" + source + ")()));"
    )
    path = scratch_file(".js", script)
    result = subprocess.run([node, str(path)], capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class FakeSheetTests(unittest.TestCase):
    """Run the generated functions against a stand-in for the page's data model."""

    rows = [["id", "status"], ["1", MISSING], ["2", PARTIAL]]

    def test_verify_fails_on_the_wrong_tab_even_when_every_cell_matches(self):
        source = sheet_js.build_verify(self.rows, [], "A1", SHEET)
        wrong = run_in_fake_sheet(source, "Sheet2", self.rows, [])
        right = run_in_fake_sheet(source, SHEET, self.rows, [])
        self.assertFalse(wrong["ok"])
        self.assertIn("Sheet2", wrong["error"])
        self.assertTrue(right["ok"], right)
        self.assertEqual(right["checked"], 6)

    def test_cf_matches_fails_a_rule_that_colors_nothing(self):
        source = sheet_js.build_cf_matches("B2:B3", SHEET, 1)
        silent = run_in_fake_sheet(source, SHEET, self.rows, [])
        working = run_in_fake_sheet(source, SHEET, self.rows, [MISSING])
        self.assertFalse(silent["ok"])
        self.assertEqual(silent["matchedCount"], 0)
        self.assertTrue(working["ok"], working)
        self.assertEqual([m["cell"] for m in working["matched"]], ["B2"])
        self.assertEqual(working["unmatchedValues"], [[PARTIAL, 1]])

    def test_cf_matches_fails_on_the_wrong_tab(self):
        source = sheet_js.build_cf_matches("B2:B3", SHEET, None)
        self.assertFalse(run_in_fake_sheet(source, "Sheet2", self.rows, [MISSING])["ok"])


class ColorResolutionTests(unittest.TestCase):
    def test_palette_rows_have_one_swatch_per_hue(self):
        for shade, swatches in sheet_js.PALETTE.items():
            self.assertEqual(len(swatches), len(sheet_js.HUES), shade)

    def test_white_and_gray_follow_the_palette_layout(self):
        self.assertEqual(sheet_js.resolve_color("white", "light"), (255, 255, 255))
        self.assertEqual(sheet_js.resolve_color("gray", "medium"), (220, 223, 228))
        with self.assertRaises(sheet_js.InputError):
            sheet_js.resolve_color("gray/light", "medium")
        with self.assertRaises(sheet_js.InputError):
            sheet_js.resolve_color("white/medium", "medium")

    def test_rejects_unknown_names(self):
        with self.assertRaises(sheet_js.InputError):
            sheet_js.resolve_color("teal", "medium")
        with self.assertRaises(sheet_js.InputError):
            sheet_js.resolve_color("red/dark", "medium")


class CommandLineTests(unittest.TestCase):
    def test_blank_verify_expects_an_empty_footprint_of_the_same_shape(self):
        path = write_json({"rows": [["a", "b"], ["c", "d"], ["e", "f"]], "links": [[1, 0, "https://x.test"]]})
        result = subprocess.run(
            ["python3", str(SCRIPT), "verify", "--input", str(path), "--anchor", "B2", "--sheet", SHEET, "--blank"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(embedded(result.stdout, "rows"), [["", ""], ["", ""], ["", ""]])
        self.assertEqual(embedded(result.stdout, "links"), [])
        self.assertEqual((embedded(result.stdout, "r0"), embedded(result.stdout, "c0")), (1, 1))

    def test_bad_input_exits_2_without_printing_javascript(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "verify", "--input", str(write_json([["a"]])), "--anchor", "A0", "--sheet", SHEET],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)

    def test_paste_and_verify_refuse_to_run_without_a_sheet_tab(self):
        for command in ("paste", "verify"):
            result = subprocess.run(
                ["python3", str(SCRIPT), command, "--input", str(write_json([["a"]])), "--anchor", "A1"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0, command)
            self.assertEqual(result.stdout, "", command)
            self.assertIn("--sheet", result.stderr, command)


if __name__ == "__main__":
    unittest.main()
