#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def parse_structured(value: str, expected_parts: int, flag: str) -> list[str]:
    parts = [part.strip() for part in value.split("|")]
    if len(parts) != expected_parts or any(not part for part in parts):
        raise argparse.ArgumentTypeError(
            f"{flag} 需要 {expected_parts} 个以 | 分隔的非空字段，当前收到: {value!r}"
        )
    return parts


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def render_composite_rows(items: Iterable[str]) -> list[str]:
    rows = []
    for index, item in enumerate(items, start=1):
        rows.append(
            f"| C{index} | {escape_cell(item)} | default / empty / long-text / disabled | before=`TODO` | TODO |"
        )
    return rows or ["| C1 | TODO | default / empty / long-text / disabled | before=`TODO` | TODO |"]


def render_interaction_rows(items: Iterable[list[str]]) -> list[str]:
    rows = []
    for index, item in enumerate(items, start=1):
        trigger_type, entry, surface, notes = item
        rows.append(
            f"| I{index} | {escape_cell(trigger_type)} | {escape_cell(entry)} | {escape_cell(surface)} | before=`TODO` / after=`TODO` | {escape_cell(notes)} |"
        )
    return rows or [
        "| I1 | TODO | TODO | TODO | before=`TODO` / after=`TODO` | TODO |"
    ]


def render_exception_rows(items: Iterable[list[str]]) -> list[str]:
    rows = []
    for index, item in enumerate(items, start=1):
        state, surface, reproduction, notes = item
        rows.append(
            f"| E{index} | {escape_cell(state)} | {escape_cell(surface)} | {escape_cell(reproduction)} | normal=`TODO` / exception=`TODO` | {escape_cell(notes)} |"
        )
    return rows or [
        "| E1 | TODO | TODO | mock / local test / browser request blocking | normal=`TODO` / exception=`TODO` | TODO |"
    ]


def render_layout_rows(items: Iterable[list[str]]) -> list[str]:
    rows = []
    for index, item in enumerate(items, start=1):
        surface, element, case, expected, observed, evidence, notes = item
        rows.append(
            f"| L{index} | {escape_cell(surface)} | {escape_cell(element)} | {escape_cell(case)} | {escape_cell(expected)} | {escape_cell(observed)} | {escape_cell(evidence)} | {escape_cell(notes)} |"
        )
    return rows or [
        "| L1 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |"
    ]


def render_breakpoint_rows(items: Iterable[list[str]]) -> list[str]:
    rows = []
    for index, item in enumerate(items, start=1):
        breakpoint, evidence, notes = item
        rows.append(
            f"| B{index} | {escape_cell(breakpoint)} | {escape_cell(evidence)} | {escape_cell(notes)} |"
        )
    return rows or [
        "| B1 | desktop | TODO | TODO |"
    ]


def render_unverified_rows(items: Iterable[list[str]]) -> list[str]:
    rows = []
    for index, item in enumerate(items, start=1):
        item_name, reason, next_step = item
        rows.append(
            f"| U{index} | {escape_cell(item_name)} | {escape_cell(reason)} | {escape_cell(next_step)} |"
        )
    return rows or [
        "| U1 | TODO | TODO | TODO |"
    ]


def build_markdown(
    page: str,
    route: str | None,
    composites: list[str],
    interactions: list[list[str]],
    exceptions: list[list[str]],
    layout_cases: list[list[str]] | None = None,
    breakpoints: list[list[str]] | None = None,
    unverified_items: list[list[str]] | None = None,
) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    route_value = route or "(not provided)"
    layout_cases = layout_cases or []
    breakpoints = breakpoints or []
    unverified_items = unverified_items or []
    lines = [
        "# Skinning Surface Manifest",
        "",
        f"- page: {page}",
        f"- route: {route_value}",
        f"- generated_at_utc: {generated_at}",
        "- safety_boundary: Exception states must be reproduced only with local, isolated test, or browser-level reversible methods. Never disturb shared services, public configuration, or real production-like data.",
        "",
        "## Composite Surfaces",
        "",
        "| ID | Surface | States To Check | Evidence | Notes |",
        "| --- | --- | --- | --- | --- |",
        *render_composite_rows(composites),
        "",
        "## Interactive Surfaces",
        "",
        "| ID | Trigger Type | Entry | Surface | Evidence | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
        *render_interaction_rows(interactions),
        "",
        "## Exception States",
        "",
        "| ID | State | Surface | Safe Reproduction | Evidence | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
        *render_exception_rows(exceptions),
        "",
        "## Content/Layout Cases",
        "",
        "| ID | Surface | Element | Case | Expected | Observed | Evidence | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        *render_layout_rows(layout_cases),
        "",
        "## Breakpoint Coverage",
        "",
        "| ID | Breakpoint | Evidence | Notes |",
        "| --- | --- | --- | --- |",
        *render_breakpoint_rows(breakpoints),
        "",
        "## Unverified Items",
        "",
        "| ID | Item | Reason | Next Step |",
        "| --- | --- | --- | --- |",
        *render_unverified_rows(unverified_items),
        "",
        "## Boundary Checks",
        "",
        "- [ ] no component replacement",
        "- [ ] no API / dataflow / route / permission changes",
        "- [ ] no copied reference source code or runtime assets",
        "- [ ] residual gaps and assumptions recorded",
        "",
        "## Exit Checklist",
        "",
        "- [ ] all key interactive surfaces enumerated or explicitly marked out of scope",
        "- [ ] content/layout cases checked for primary content, help text, and error copy",
        "- [ ] claims limited to states with real rendered evidence",
        "- [ ] manifest updated with evidence or explicit unverified reasons",
        "",
        "## Verification Notes",
        "",
        "- minimal verification:",
        "- breakpoints checked: desktop=`TODO`",
        "- remaining visual gaps:",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a markdown manifest for composite, interactive, and exception surfaces."
    )
    parser.add_argument("--page", required=True, help="Target page or flow name.")
    parser.add_argument("--route", help="Target route or entry path.")
    parser.add_argument(
        "--composite",
        action="append",
        default=[],
        help="Composite surface label. Repeat the flag for multiple items.",
    )
    parser.add_argument(
        "--interaction",
        action="append",
        default=[],
        metavar="TRIGGER|ENTRY|SURFACE|NOTES",
        help="Interactive surface definition. Example: click|修改密码|modal|账号设置页右上角",
    )
    parser.add_argument(
        "--exception",
        action="append",
        default=[],
        metavar="STATE|SURFACE|SAFE_REPRODUCTION|NOTES",
        help="Exception surface definition. Example: backend-unavailable|page-banner|browser request blocking|登录页顶部告警",
    )
    parser.add_argument(
        "--layout-case",
        action="append",
        default=[],
        metavar="SURFACE|ELEMENT|CASE|EXPECTED|OBSERVED|EVIDENCE|NOTES",
        help="Content/layout case definition. Example: 筛选栏|select trigger|long selected value|主文案可读|仅显示前3字|before=`TODO` / after=`TODO`|需增宽 panel",
    )
    parser.add_argument(
        "--breakpoint",
        action="append",
        default=[],
        metavar="BREAKPOINT|EVIDENCE|NOTES",
        help="Breakpoint coverage. Example: desktop|before=`TODO` / after=`TODO`|1440 宽度回看",
    )
    parser.add_argument(
        "--unverified",
        action="append",
        default=[],
        metavar="ITEM|REASON|NEXT_STEP",
        help="Unverified item. Example: 二级编辑页|本地环境未启动成功|待环境可用后回看",
    )
    parser.add_argument("--output", help="Write the manifest to this path instead of stdout.")
    args = parser.parse_args()

    interactions = [
        parse_structured(value, expected_parts=4, flag="--interaction")
        for value in args.interaction
    ]
    exceptions = [
        parse_structured(value, expected_parts=4, flag="--exception")
        for value in args.exception
    ]
    layout_cases = [
        parse_structured(value, expected_parts=7, flag="--layout-case")
        for value in args.layout_case
    ]
    breakpoints = [
        parse_structured(value, expected_parts=3, flag="--breakpoint")
        for value in args.breakpoint
    ]
    unverified_items = [
        parse_structured(value, expected_parts=3, flag="--unverified")
        for value in args.unverified
    ]

    markdown = build_markdown(
        page=args.page,
        route=args.route,
        composites=args.composite,
        interactions=interactions,
        exceptions=exceptions,
        layout_cases=layout_cases,
        breakpoints=breakpoints,
        unverified_items=unverified_items,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
