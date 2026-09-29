"""Guard the wecom-cli request builder and read-back comparator.

The failure modes worth pinning are the silent ones observed on the live API: a
leading-zero ID that the sheet stores as a number, a select value that the API accepts
and then drops, a link whose text survives while its URL does not, a write that lands
one column off, and a response read without mode "default" that carries no grid.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cli_grid.py"
SPEC = importlib.util.spec_from_file_location("cli_grid", SCRIPT)
cli_grid = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli_grid)

ROWS = [["ID", "Status"], ["007", "进行中"]]
LINKS = [[1, 0, "https://example.com/7"]]


def cell(value: dict) -> dict:
    return {"cell_value": value, "cell_format": {}}


def readback(grid_rows, errcode=0) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump({"errcode": errcode, "grid_data": {"rows": [{"values": r} for r in grid_rows]}}, handle, ensure_ascii=False)
    handle.close()
    return Path(handle.name)


class RequestTests(unittest.TestCase):
    def test_anchor_offsets_and_cell_types(self):
        body, warnings = cli_grid.build_request(ROWS, LINKS, "C3", "doc", "s1")
        grid = body["grid_data"]
        self.assertEqual((grid["start_row"], grid["start_column"]), (2, 2))
        first = grid["rows"][1]["values"]
        self.assertEqual(first[0]["data_type"], "LINK")
        self.assertEqual(first[0]["cell_value"]["link"], {"text": "007", "url": "https://example.com/7"})
        self.assertEqual(first[1]["data_type"], "TEXT")
        self.assertEqual(warnings, [])

    def test_never_writes_select_types(self):
        body, _ = cli_grid.build_request(ROWS, [], "A1", "doc", "s1")
        types = {v["data_type"] for r in body["grid_data"]["rows"] for v in r["values"]}
        self.assertEqual(types, {"TEXT"})

    def test_warns_about_number_like_text(self):
        _, warnings = cli_grid.build_request([["007", "1.50", "1234567890123456", "7", "2026-09-28"]], [], "A1", "d", "s")
        flagged = [w.split()[0] for w in warnings]
        self.assertEqual(flagged, ["A1", "B1", "C1"])

    def test_readback_range_adds_one_row_and_column(self):
        self.assertEqual(cli_grid.readback_range(ROWS, "B2"), "B2:D4")


class VerifyTests(unittest.TestCase):
    def good_grid(self):
        return [
            [cell({"text": "ID"}), cell({"text": "Status"}), cell({})],
            [cell({"link": {"text": "007", "url": "https://example.com/7"}}),
             cell({"select": {"value": ["进行中"]}}), cell({})],
        ]

    def test_exact_match_passes_and_missing_border_cells_count_as_empty(self):
        result = cli_grid.verify(ROWS, LINKS, "A1", self.good_grid(), blank=False)
        self.assertTrue(result["ok"], result)
        self.assertEqual((result["compared"], result["linksChecked"]), (4, 1))

    def test_leading_zero_stored_as_number_is_a_diff(self):
        grid = self.good_grid()
        grid[1][0] = cell({"number": 7.0})
        result = cli_grid.verify(ROWS, [], "A1", grid, blank=False)
        self.assertEqual(result["diffs"], [{"cell": "A2", "expected": "007", "actual": "7"}])

    def test_dropped_select_value_is_a_diff(self):
        grid = self.good_grid()
        grid[1][1] = cell({})
        result = cli_grid.verify(ROWS, LINKS, "A1", grid, blank=False)
        self.assertEqual([d["cell"] for d in result["diffs"]], ["B2"])

    def test_link_url_mismatch_and_spill_are_reported(self):
        grid = self.good_grid()
        grid[1][0] = cell({"link": {"text": "007", "url": "https://example.com/8"}})
        grid.append([cell({"text": "stray"})])
        result = cli_grid.verify(ROWS, LINKS, "A1", grid, blank=False)
        self.assertEqual(result["linkDiffs"][0]["actual"], "https://example.com/8")
        self.assertEqual(result["spill"], [{"cell": "A3", "actual": "stray"}])
        self.assertFalse(result["ok"])

    def test_blank_mode_flags_any_content(self):
        result = cli_grid.verify(ROWS, [], "A1", [[cell({}), cell({"number": 3.5})]], blank=True)
        self.assertEqual(result["diffs"], [{"cell": "B1", "actual": "3.5"}])

    def test_response_without_grid_is_rejected(self):
        path = readback([])
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.pop("grid_data")
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(cli_grid.InputError):
            cli_grid.load_readback(path)
        path.unlink()

    def test_error_response_is_rejected(self):
        path = readback([], errcode=851008)
        with self.assertRaises(cli_grid.InputError):
            cli_grid.load_readback(path)
        path.unlink()


if __name__ == "__main__":
    unittest.main()
