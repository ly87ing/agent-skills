#!/usr/bin/env python3
"""Validate structural and offline-delivery invariants in an SVG diagram.

The validator is intentionally narrower than a renderer. It catches malformed XML,
an invalid or missing viewBox, duplicate IDs, broken local URL/href/ARIA references,
and non-local dependencies. It cannot prove visual layout, accessibility, factual
correctness, or whether active content is safe.

A link (`<a href>`) is navigation, not a dependency: it may point at a detail card
elsewhere in the host page or at a source file, and the diagram renders the same
whether or not its target is reachable. Links are counted, never failed, except for
active schemes such as javascript:. Everything that must load for the diagram to
render (`use`, `image`, markers and paints through `url()`, `@import`, stylesheets,
`src`) is still checked.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


URL_PATTERN = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
IMPORT_PATTERN = re.compile(r"@import\s+(?:url\(\s*)?(['\"])(.*?)\1", re.IGNORECASE)
XML_STYLESHEET_PATTERN = re.compile(r"<\?xml-stylesheet\b(.*?)\?>", re.IGNORECASE | re.DOTALL)
XML_STYLESHEET_HREF_PATTERN = re.compile(
    r"\bhref\s*=\s*(['\"])(.*?)\1",
    re.IGNORECASE | re.DOTALL,
)
IDREF_ATTRIBUTES = {"aria-describedby", "aria-labelledby"}
RESOURCE_ATTRIBUTES = {"data", "href", "poster", "src"}
NAVIGATION_ELEMENTS = {"a"}
DANGEROUS_SCHEMES = ("javascript:", "vbscript:")
MAX_DIAGNOSTICS = 50


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def parse_viewbox(raw: str | None) -> tuple[float, float, float, float] | None:
    if raw is None:
        return None
    parts = [part for part in re.split(r"[\s,]+", raw.strip()) if part]
    if len(parts) != 4:
        return None
    try:
        values = tuple(float(part) for part in parts)
    except ValueError:
        return None
    if not all(math.isfinite(value) for value in values):
        return None
    if values[2] <= 0 or values[3] <= 0:
        return None
    return values


def classify_reference(
    raw: str,
    local_references: set[str],
    non_local_references: set[str],
    errors: list[str],
) -> None:
    target = raw.strip().strip("'\"")
    if not target:
        return
    lowered = target.lower()
    if lowered.startswith(DANGEROUS_SCHEMES):
        errors.append(f"active reference is not allowed: {target}")
    elif target.startswith("#"):
        if len(target) == 1:
            errors.append("empty local reference: #")
        else:
            local_references.add(target[1:])
    elif not lowered.startswith("data:"):
        non_local_references.add(target)


def classify_link(raw: str, links: set[str], errors: list[str]) -> None:
    target = raw.strip()
    if target.lower().startswith(DANGEROUS_SCHEMES):
        errors.append(f"active reference is not allowed: {target}")
    elif target:
        links.add(target)


def inspect_reference_value(
    value: str,
    local_references: set[str],
    non_local_references: set[str],
    errors: list[str],
) -> None:
    for match in URL_PATTERN.finditer(value):
        classify_reference(match.group(2), local_references, non_local_references, errors)
    for match in IMPORT_PATTERN.finditer(value):
        classify_reference(match.group(2), local_references, non_local_references, errors)


def validate_svg(path: Path, allow_external: bool) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read UTF-8 SVG: {exc}"], {}

    if re.search(r"<!DOCTYPE\b", source, re.IGNORECASE):
        return ["DOCTYPE declarations are not allowed"], {}

    stylesheet_references: list[str] = []
    for instruction in XML_STYLESHEET_PATTERN.finditer(source):
        href = XML_STYLESHEET_HREF_PATTERN.search(instruction.group(1))
        if href is None or not href.group(2).strip():
            errors.append("xml-stylesheet processing instruction requires a quoted href")
        else:
            stylesheet_references.append(href.group(2))

    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        return [f"malformed XML: {exc}"], {}

    if local_name(root.tag) != "svg":
        errors.append(f"root element is {local_name(root.tag)!r}, expected 'svg'")

    viewbox = parse_viewbox(root.attrib.get("viewBox"))
    if viewbox is None:
        errors.append("viewBox must contain four finite numbers with positive width and height")

    identifiers: set[str] = set()
    local_references: set[str] = set()
    non_local_references: set[str] = set()
    links: set[str] = set()

    for reference in stylesheet_references:
        classify_reference(reference, local_references, non_local_references, errors)

    for element in root.iter():
        identifier = element.attrib.get("id")
        if identifier:
            if identifier in identifiers:
                errors.append(f"duplicate id: {identifier}")
            identifiers.add(identifier)

        for attribute, value in element.attrib.items():
            attribute_name = local_name(attribute)
            if attribute_name == "href" and local_name(element.tag) in NAVIGATION_ELEMENTS:
                classify_link(value, links, errors)
            elif attribute_name in RESOURCE_ATTRIBUTES:
                classify_reference(value, local_references, non_local_references, errors)
            elif attribute_name in IDREF_ATTRIBUTES:
                local_references.update(reference for reference in value.split() if reference)
            inspect_reference_value(value, local_references, non_local_references, errors)

        if local_name(element.tag) == "style":
            inspect_reference_value(
                "".join(element.itertext()),
                local_references,
                non_local_references,
                errors,
            )

    for missing in sorted(local_references - identifiers):
        errors.append(f"missing referenced id: {missing}")
    if non_local_references and not allow_external:
        for target in sorted(non_local_references):
            errors.append(f"non-local dependency requires --allow-external: {target}")

    unique_errors = list(dict.fromkeys(errors))
    stats: dict[str, object] = {
        "ids": len(identifiers),
        "local_references": len(local_references),
        "non_local_references": len(non_local_references),
        "links": len(links),
        "viewbox": viewbox,
    }
    return unique_errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate structural and offline-delivery invariants in an SVG diagram."
    )
    parser.add_argument("svg", type=Path, help="SVG file to validate")
    parser.add_argument(
        "--allow-external",
        action="store_true",
        help="permit non-fragment, non-data dependencies selected by the user",
    )
    args = parser.parse_args()

    errors, stats = validate_svg(args.svg, args.allow_external)
    if errors:
        print(f"INVALID {args.svg}", file=sys.stderr)
        for diagnostic in errors[:MAX_DIAGNOSTICS]:
            print(f"- {diagnostic}", file=sys.stderr)
        if len(errors) > MAX_DIAGNOSTICS:
            print(
                f"- {len(errors) - MAX_DIAGNOSTICS} additional diagnostic(s) omitted",
                file=sys.stderr,
            )
        return 1

    viewbox = " ".join(f"{value:g}" for value in stats["viewbox"])
    print(
        f"OK {args.svg}: viewBox={viewbox}; ids={stats['ids']}; "
        f"local_refs={stats['local_references']}; external_refs={stats['non_local_references']}; "
        f"links={stats['links']} (targets not checked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
