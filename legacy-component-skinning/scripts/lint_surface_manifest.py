#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "## Composite Surfaces",
    "## Interactive Surfaces",
    "## Exception States",
    "## Content/Layout Cases",
    "## Breakpoint Coverage",
    "## Unverified Items",
    "## Exit Checklist",
]

REQUIRED_EXIT_ITEMS = [
    "all key interactive surfaces enumerated or explicitly marked out of scope",
    "content/layout cases checked for primary content, help text, and error copy",
    "claims limited to states with real rendered evidence",
    "manifest updated with evidence or explicit unverified reasons",
]


def validate_manifest_text(text: str) -> list[str]:
    errors: list[str] = []

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing required section: {section}")

    if "TODO" in text:
        errors.append("manifest still contains TODO placeholders")

    for item in REQUIRED_EXIT_ITEMS:
        checked = f"- [x] {item}"
        checked_upper = f"- [X] {item}"
        if checked not in text and checked_upper not in text:
            errors.append(f"exit checklist item is not checked: {item}")

    layout_rows = re.findall(r"^\| L\d+ \|", text, re.MULTILINE)
    if not layout_rows:
        errors.append("content/layout cases section has no recorded rows")

    breakpoint_rows = re.findall(r"^\| B\d+ \|", text, re.MULTILINE)
    if not breakpoint_rows:
        errors.append("breakpoint coverage section has no recorded rows")

    unverified_rows = re.findall(r"^\| U\d+ \|", text, re.MULTILINE)
    if not unverified_rows:
        errors.append("unverified items section has no recorded rows")

    if re.search(r"^\| U\d+ \| none \| fully verified \| n/a \|$", text, re.MULTILINE) is None:
        if "## Unverified Items" in text and "fully verified" not in text and not unverified_rows:
            errors.append("unverified items must record rows or explicitly say fully verified")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a filled skinning surface manifest before claiming completion."
    )
    parser.add_argument("manifest", help="Path to the markdown manifest to validate.")
    args = parser.parse_args()

    text = Path(args.manifest).read_text(encoding="utf-8")
    errors = validate_manifest_text(text)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: manifest is complete enough for review/claim usage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
