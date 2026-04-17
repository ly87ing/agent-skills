#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def render_value(value: str | None, placeholder: str = "TODO") -> str:
    if value is None or not value.strip():
        return placeholder
    return value.strip()


def render_list(items: list[str], placeholder: str = "TODO") -> list[str]:
    if not items:
        return [f"- {placeholder}"]
    return [f"- {item.strip()}" for item in items if item.strip()] or [f"- {placeholder}"]


def build_markdown(args: argparse.Namespace) -> str:
    lines = [
        "# Safe Merge Review Summary",
        "",
        f"- repo: {render_value(args.repo)}",
        f"- current branch: {render_value(args.current_branch)}",
        f"- source ref: {render_value(args.source_ref)}",
        f"- merge base: {render_value(args.merge_base)}",
        f"- left/right counts: {render_value(args.left_right_counts)}",
        f"- merge strategy: {render_value(args.merge_strategy)}",
        f"- completeness proof: {render_value(args.completeness_proof)}",
        f"- semantic review conclusion: {render_value(args.semantic_review)}",
        f"- push status: {render_value(args.push_status)}",
        "",
        "## Incoming key commits",
        "",
        *render_list(args.incoming_commit),
        "",
        "## Hotspot overlap files",
        "",
        *render_list(args.hotspot),
        "",
        "## Conflicted files and reasoning",
        "",
        *render_list(args.conflict),
        "",
        "## Verification command(s)",
        "",
        *render_list(args.verification),
        "",
        "## Residual risks",
        "",
        *render_list(args.risk, placeholder="none recorded"),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a markdown evidence summary for safe merge review."
    )
    parser.add_argument("--repo")
    parser.add_argument("--current-branch")
    parser.add_argument("--source-ref")
    parser.add_argument("--merge-base")
    parser.add_argument("--left-right-counts")
    parser.add_argument("--merge-strategy")
    parser.add_argument("--completeness-proof")
    parser.add_argument("--semantic-review")
    parser.add_argument("--push-status")
    parser.add_argument("--incoming-commit", action="append", default=[])
    parser.add_argument("--hotspot", action="append", default=[])
    parser.add_argument("--conflict", action="append", default=[])
    parser.add_argument("--verification", action="append", default=[])
    parser.add_argument("--risk", action="append", default=[])
    parser.add_argument("--output")
    args = parser.parse_args()

    markdown = build_markdown(args) + "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
