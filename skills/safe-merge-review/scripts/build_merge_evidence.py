#!/usr/bin/env python3
"""Render a deterministic Safe Merge Review evidence summary from CLI-supplied fields.

Each Reporting field maps to a flag; unset scalar fields render as TODO (residual
risks as "none recorded"). With --collect, the script derives read-only Git facts
from --repo and --source-ref and bounds long commit/hotspot lists. It prints markdown
to stdout, or writes it to --output PATH. Standard library only.

Proof method has no default on purpose. Collection fills it only when both ancestry
and an empty remaining range prove inclusion; squash merges still require an explicit
alternative proof.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def render_value(value: str | None, placeholder: str = "TODO") -> str:
    if value is None or not value.strip():
        return placeholder
    return value.strip()


def render_list(items: list[str], placeholder: str = "TODO") -> list[str]:
    if not items:
        return [f"- {placeholder}"]
    return [f"- {item.strip()}" for item in items if item.strip()] or [f"- {placeholder}"]


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return result


def bounded(items: list[str], maximum: int, label: str, risks: list[str]) -> list[str]:
    if len(items) <= maximum:
        return items
    risks.append(f"{label} truncated to {maximum} of {len(items)} items")
    return items[:maximum]


def collect_git_evidence(args: argparse.Namespace) -> None:
    if not args.repo or not args.source_ref:
        raise ValueError("--collect requires --repo and --source-ref")
    if args.source_ref.startswith("-") or any(char in args.source_ref for char in "\r\n\0"):
        raise ValueError("source ref must not start with '-' or contain control characters")
    if args.max_items < 1:
        raise ValueError("--max-items must be at least 1")

    requested_repo = Path(args.repo).expanduser().resolve()
    root_result = run_git(requested_repo, "rev-parse", "--show-toplevel", check=False)
    if root_result.returncode != 0:
        raise ValueError(f"repo is not a git worktree: {requested_repo}")
    repo = Path(root_result.stdout.strip()).resolve()

    source_result = run_git(repo, "rev-parse", "--verify", f"{args.source_ref}^{{commit}}", check=False)
    if source_result.returncode != 0:
        raise ValueError(f"source ref is not a commit: {args.source_ref}")

    base_result = run_git(repo, "merge-base", "HEAD", args.source_ref, check=False)
    if base_result.returncode != 0 or not base_result.stdout.strip():
        raise ValueError(f"HEAD and {args.source_ref} have no merge base")
    merge_base = base_result.stdout.strip()

    branch = run_git(repo, "branch", "--show-current").stdout.strip()
    if not branch:
        short_head = run_git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        branch = f"HEAD (detached at {short_head})"

    dirty_lines = run_git(repo, "status", "--porcelain=v1").stdout.splitlines()
    incoming = run_git(repo, "log", "--format=%h %s", f"HEAD..{args.source_ref}").stdout.splitlines()
    current_paths = set(run_git(repo, "diff", "--name-only", f"{merge_base}..HEAD").stdout.splitlines())
    source_paths = set(
        run_git(repo, "diff", "--name-only", f"{merge_base}..{args.source_ref}").stdout.splitlines()
    )

    args.repo = str(repo)
    args.current_branch = branch
    args.merge_base = merge_base
    args.left_right_counts = run_git(
        repo, "rev-list", "--left-right", "--count", f"HEAD...{args.source_ref}"
    ).stdout.strip()
    args.dirty_worktree = "clean" if not dirty_lines else "dirty: " + "; ".join(dirty_lines)
    args.incoming_commit = bounded(incoming, args.max_items, "incoming commits", args.risk)
    args.hotspot = bounded(sorted(current_paths & source_paths), args.max_items, "hotspots", args.risk)

    ancestor = run_git(repo, "merge-base", "--is-ancestor", args.source_ref, "HEAD", check=False)
    if ancestor.returncode == 0 and not incoming:
        args.completeness_proof = (
            f"{args.source_ref} is an ancestor of HEAD and HEAD..{args.source_ref} is empty"
        )
        args.proof_method = "is-ancestor"
    else:
        args.completeness_proof = None
        args.proof_method = None


def build_markdown(args: argparse.Namespace) -> str:
    lines = [
        "# Safe Merge Review Summary",
        "",
        f"- repo: {render_value(args.repo)}",
        f"- current branch: {render_value(args.current_branch)}",
        f"- source ref: {render_value(args.source_ref)}",
        f"- merge base: {render_value(args.merge_base)}",
        f"- left/right counts: {render_value(args.left_right_counts)}",
        f"- dirty worktree status: {render_value(args.dirty_worktree)}",
        f"- merge strategy: {render_value(args.merge_strategy)}",
        f"- completeness proof: {render_value(args.completeness_proof)}",
        f"- proof method: {render_value(args.proof_method)}",
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


VALID_PROOF_METHODS = {"is-ancestor", "patch-equivalent", "tree-diff", "cherry-pick-noop"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a markdown evidence summary for safe merge review."
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="derive read-only Git facts from --repo and --source-ref",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=20,
        help="maximum collected incoming commits or hotspots to render (default: 20)",
    )
    parser.add_argument("--repo")
    parser.add_argument("--current-branch")
    parser.add_argument("--source-ref")
    parser.add_argument("--merge-base")
    parser.add_argument("--left-right-counts")
    parser.add_argument("--dirty-worktree")
    parser.add_argument("--merge-strategy")
    parser.add_argument("--completeness-proof")
    parser.add_argument("--proof-method", choices=sorted(VALID_PROOF_METHODS))
    parser.add_argument("--semantic-review")
    parser.add_argument("--push-status")
    parser.add_argument("--incoming-commit", action="append", default=[])
    parser.add_argument("--hotspot", action="append", default=[])
    parser.add_argument("--conflict", action="append", default=[])
    parser.add_argument("--verification", action="append", default=[])
    parser.add_argument("--risk", action="append", default=[])
    parser.add_argument("--output")
    args = parser.parse_args()

    if args.collect:
        try:
            collect_git_evidence(args)
        except ValueError as exc:
            parser.error(str(exc))

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
