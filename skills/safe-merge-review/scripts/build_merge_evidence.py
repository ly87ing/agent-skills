#!/usr/bin/env python3
"""Render a deterministic Safe Merge Review evidence summary from CLI-supplied fields.

Each Reporting field maps to a flag; unset fields render as TODO (residual risks as
"none recorded"). With --collect, the script derives read-only Git facts from --repo,
--source-ref and --target-ref (default HEAD) and bounds long commit/hotspot lists.
After the merge, pass --pre-merge-ref so the diff model is computed against the target
as it was before the merge while completeness is proved against the target as it is
now. Values passed by flag are never overwritten by collection, and a collected list
that is genuinely empty renders as "none", not TODO. It prints markdown to stdout, or
writes it to --output PATH. Standard library only.

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


def check_ref(repo: Path, label: str, ref: str) -> None:
    if ref.startswith("-") or any(char in ref for char in "\r\n\0"):
        raise ValueError(f"{label} must not start with '-' or contain control characters")
    if run_git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False).returncode != 0:
        raise ValueError(f"{label} is not a commit: {ref}")


def collect_list(
    args: argparse.Namespace, field: str, items: list[str], label: str
) -> None:
    """Fill a list field from Git unless the caller already passed it by flag."""
    if getattr(args, field):
        return
    setattr(args, field, bounded(items, args.max_items, label, args.risk))
    args.collected.add(field)


def collect_git_evidence(args: argparse.Namespace) -> None:
    if not args.repo or not args.source_ref:
        raise ValueError("--collect requires --repo and --source-ref")
    if args.max_items < 1:
        raise ValueError("--max-items must be at least 1")

    requested_repo = Path(args.repo).expanduser().resolve()
    root_result = run_git(requested_repo, "rev-parse", "--show-toplevel", check=False)
    if root_result.returncode != 0:
        raise ValueError(f"repo is not a git worktree: {requested_repo}")
    repo = Path(root_result.stdout.strip()).resolve()

    source, target, pre_merge = args.source_ref, args.target_ref, args.pre_merge_ref
    check_ref(repo, "source ref", source)
    check_ref(repo, "target ref", target)
    if pre_merge:
        check_ref(repo, "pre-merge ref", pre_merge)
    model = pre_merge or target

    base_result = run_git(repo, "merge-base", model, source, check=False)
    if base_result.returncode != 0 or not base_result.stdout.strip():
        raise ValueError(f"{model} and {source} have no merge base")
    merge_base = base_result.stdout.strip()

    if target == "HEAD":
        branch = run_git(repo, "branch", "--show-current").stdout.strip()
        if not branch:
            short_head = run_git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
            branch = f"HEAD (detached at {short_head})"
    else:
        branch = target

    dirty_lines = run_git(repo, "status", "--porcelain=v1").stdout.splitlines()
    incoming = run_git(repo, "log", "--format=%h %s", f"{model}..{source}").stdout.splitlines()
    target_paths = set(run_git(repo, "diff", "--name-only", f"{merge_base}..{model}").stdout.splitlines())
    source_paths = set(run_git(repo, "diff", "--name-only", f"{merge_base}..{source}").stdout.splitlines())

    args.repo = str(repo)
    args.target = args.target or branch
    args.merge_base = args.merge_base or merge_base
    args.left_right_counts = args.left_right_counts or run_git(
        repo, "rev-list", "--left-right", "--count", f"{model}...{source}"
    ).stdout.strip()
    args.dirty_worktree = args.dirty_worktree or (
        "clean" if not dirty_lines else "dirty: " + "; ".join(dirty_lines)
    )
    collect_list(args, "incoming_commit", incoming, "incoming commits")
    collect_list(args, "hotspot", sorted(target_paths & source_paths), "hotspots")
    if pre_merge:
        landed = run_git(repo, "diff", "--name-only", f"{pre_merge}..{target}").stdout.splitlines()
        collect_list(args, "landed_file", landed, "landed files")

    remaining = run_git(repo, "log", "--format=%h", f"{target}..{source}").stdout.splitlines()
    ancestor = run_git(repo, "merge-base", "--is-ancestor", source, target, check=False)
    if ancestor.returncode == 0 and not remaining:
        if not args.completeness_proof and not args.proof_method:
            args.completeness_proof = f"{source} is an ancestor of {target} and {target}..{source} is empty"
            args.proof_method = "is-ancestor"
    elif pre_merge and not args.proof_method:
        args.risk.append(
            f"{source} is not an ancestor of {target}; prove completeness with "
            "patch-equivalent, tree-diff, or cherry-pick-noop before calling the merge complete"
        )


def build_markdown(args: argparse.Namespace) -> str:
    def items(field: str) -> list[str]:
        placeholder = "none" if field in args.collected else "TODO"
        return render_list(getattr(args, field), placeholder)

    lines = [
        "# Safe Merge Review Summary",
        "",
        f"- repo: {render_value(args.repo)}",
        f"- target: {render_value(args.target)}",
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
        *items("incoming_commit"),
        "",
        "## Hotspot overlap files",
        "",
        *items("hotspot"),
        "",
        "## Landed files",
        "",
        *items("landed_file"),
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
        help="maximum collected incoming commits, hotspots, or landed files to render (default: 20)",
    )
    parser.add_argument(
        "--target-ref",
        default="HEAD",
        help="ref the source merges into; completeness is proved against it (default: HEAD)",
    )
    parser.add_argument(
        "--pre-merge-ref",
        help="the target before the merge (HEAD^1 of a merge commit, or the sha saved before a "
        "fast-forward or squash); the diff model uses it and landed files are listed",
    )
    parser.add_argument("--repo")
    parser.add_argument("--target", help="the branch the source merges into, when not collected")
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
    parser.add_argument("--landed-file", action="append", default=[])
    parser.add_argument("--conflict", action="append", default=[])
    parser.add_argument("--verification", action="append", default=[])
    parser.add_argument("--risk", action="append", default=[])
    parser.add_argument("--output")
    args = parser.parse_args()
    args.collected = set()

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
