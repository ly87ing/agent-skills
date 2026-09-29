#!/usr/bin/env python3
"""Build wecom-cli write requests for a block of rows and verify the cells read back.

The block file is the same one `sheet_js.py` takes: a CSV, a JSON list of rows, or
`{"rows": [...], "links": [[row, col, url], ...]}` with zero-based positions.

Subcommands:
  request  print the JSON body for `wecom-cli sheet contents update --json`, writing
           every cell as TEXT (or LINK), never as SELECT/CHECKBOX
  range    print the A1 range to read back: the block plus one column to its right
           and one row below it
  verify   compare a saved `wecom-cli sheet ranges get` response (mode "default", the
           range printed by `range`) with the block; with --blank, prove the same cells
           are empty before writing
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("sheet_js", Path(__file__).with_name("sheet_js.py"))
sheet_js = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sheet_js)

InputError = sheet_js.InputError

# Text the sheet stores as a number and then shows differently, even in a cell formatted
# as text (observed: "007" -> 7, "1.50" -> 1.5; a 16-digit number came back unchanged).
NUMBER_LIKE = re.compile(r"[+-]?(0\d+(\.\d*)?|\d+\.\d*0)")


def cell_text(cell: dict) -> tuple[str, str | None]:
    value = cell.get("cell_value") or {}
    if "link" in value:
        link = value["link"] or {}
        return str(link.get("text", "")), str(link.get("url", ""))
    if "text" in value:
        return str(value["text"]), None
    if "number" in value:
        number = value["number"]
        if isinstance(number, float) and number.is_integer():
            number = int(number)
        return str(number), None
    if "select" in value:
        return ",".join(str(v) for v in (value["select"] or {}).get("value") or []), None
    if "formula" in value:
        return str(value["formula"]), None
    return "", None


def build_request(rows, links, anchor: str, docid: str, sheet_id: str) -> tuple[dict, list[str]]:
    r0, c0 = sheet_js.parse_cell(anchor)
    link_at = {(r, c): url for r, c, url in links}
    out_rows, warnings = [], []
    for r, row in enumerate(rows):
        values = []
        for c, text in enumerate(row):
            if (r, c) in link_at:
                values.append({"data_type": "LINK", "cell_value": {"link": {"text": text, "url": link_at[(r, c)]}}, "cell_format": {}})
            else:
                values.append({"data_type": "TEXT", "cell_value": {"text": text}, "cell_format": {}})
                if NUMBER_LIKE.fullmatch(text):
                    warnings.append(f"{sheet_js.to_a1(r0 + r, c0 + c)} {text!r} will be stored as a number and read back changed")
        out_rows.append({"values": values})
    body = {"docid": docid, "sheet_id": sheet_id, "grid_data": {"start_row": r0, "start_column": c0, "rows": out_rows}}
    return body, warnings


def readback_range(rows, anchor: str) -> str:
    r0, c0 = sheet_js.parse_cell(anchor)
    return f"{sheet_js.to_a1(r0, c0)}:{sheet_js.to_a1(r0 + len(rows), c0 + len(rows[0]))}"


def load_readback(path: Path) -> list[list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    error = payload.get("error")
    if isinstance(error, dict):
        raise InputError(f"read-back failed: {error.get('code')} {error.get('message', '')}; read again")
    if payload.get("errcode") not in (0, None):
        raise InputError(f"read-back failed: errcode {payload.get('errcode')} {payload.get('errmsg', '')}")
    grid = payload.get("grid_data")
    if not isinstance(grid, dict):
        raise InputError("read-back has no grid_data; run `sheet ranges get` with mode \"default\" and the range from `range`")
    return [row.get("values") or [] for row in grid.get("rows") or []]


def verify(rows, links, anchor: str, grid: list[list[dict]], blank: bool) -> dict:
    r0, c0 = sheet_js.parse_cell(anchor)
    height, width = len(rows), len(rows[0])
    link_at = {(r, c): url for r, c, url in links}

    def at(r, c):
        cell = grid[r][c] if r < len(grid) and c < len(grid[r]) else {}
        return cell_text(cell)

    diffs, link_diffs, spill = [], [], []
    for r in range(height + 1):
        for c in range(width + 1):
            text, url = at(r, c)
            name = sheet_js.to_a1(r0 + r, c0 + c)
            if blank or r == height or c == width:
                if text:
                    (diffs if blank else spill).append({"cell": name, "actual": text})
                continue
            if text != rows[r][c]:
                diffs.append({"cell": name, "expected": rows[r][c], "actual": text})
            if (r, c) in link_at and url != link_at[(r, c)]:
                link_diffs.append({"cell": name, "expected": link_at[(r, c)], "actual": url})
    return {
        "ok": not (diffs or link_diffs or spill),
        "mode": "blank" if blank else "verify",
        "compared": height * width,
        "linksChecked": 0 if blank else len(links),
        "diffs": diffs,
        "linkDiffs": link_diffs,
        "spill": spill,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("request", "range", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--input", required=True, type=Path)
        p.add_argument("--anchor", required=True)
        if name == "request":
            p.add_argument("--docid", required=True, help="docid or sheet URL")
            p.add_argument("--sheet-id", required=True, help="sheet_id from `wecom-cli sheet get`")
        if name == "verify":
            p.add_argument("--readback", required=True, type=Path, help="saved `sheet ranges get` response")
            p.add_argument("--blank", action="store_true", help="require the block and its borders to be empty")
    args = parser.parse_args(argv)
    try:
        rows, links, changed = sheet_js.load_block(args.input)
        if args.command == "request":
            body, warnings = build_request(rows, links, args.anchor, args.docid, args.sheet_id)
            if changed:
                warnings.append(f"{changed} cell(s) had tabs or line breaks replaced with spaces")
            for warning in warnings:
                print("warning: " + warning, file=sys.stderr)
            print(json.dumps(body, ensure_ascii=False))
        elif args.command == "range":
            print(readback_range(rows, args.anchor))
        else:
            result = verify(rows, links, args.anchor, load_readback(args.readback), args.blank)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["ok"] else 1
    except (InputError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
