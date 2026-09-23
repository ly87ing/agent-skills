#!/usr/bin/env python3
"""Observe skill loading in a real Codex run with the active catalog.

The metadata-only judge in run_trigger_evals.py answers a useful but artificial
single-choice question. Codex may load several skills for one request, and the
neighbouring skills that affect that decision come from the user's actual runtime
configuration. This runner therefore launches `codex exec` in a fresh empty
directory, keeps the sandbox read-only, and records every SKILL.md that Codex reads.

Before running, it verifies that the selected maintained skill packages match an
installed package under ~/.codex/skills or ~/.agents/skills (or a root supplied with
--installed-root). This prevents a green result from silently exercising a stale
managed checkout instead of the source under review.

Routing and output quality remain separate claims. A positive eval passes routing
when its maintained skill is among the skills Codex actually reads; a negative eval
passes when that skill is absent. Use --show-responses to read the final answers
against expected_output. The runner does not reduce answer quality to brittle phrase
matching or claim that a route pass proves the behavior. Only show transcripts for
self-contained evals whose inputs and possible ambient-runtime findings are safe to
print.

Usage:
  python3 tools/evals/run_codex_catalog_evals.py --case artifact-hygiene:19
  python3 tools/evals/run_codex_catalog_evals.py \\
    --case verification:19 --case reader-facing-writing:38 \\
    --show-responses

Exit code: 0 when every selected routing expectation passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EVALS_DIR = Path(__file__).resolve().parent
ROOT = EVALS_DIR.parents[1]
SKILLS = ROOT / "skills"
if str(EVALS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALS_DIR))

import run_trigger_evals as trigger  # noqa: E402


CODEX_TIMEOUT_SECONDS = 300
AUTH_STATUS_TIMEOUT_SECONDS = 10
RUNTIME_RESOURCE_DIRS = ("assets", "references", "scripts")
SKILL_PATH_PATTERN = re.compile(
    r"(?<![a-z0-9-])([a-z0-9]+(?:-[a-z0-9]+)*)/SKILL\.md"
)


def codex_auth_problem() -> str | None:
    """Return a recovery message when Codex explicitly reports no login."""
    try:
        result = subprocess.run(
            ["codex", "login", "status"],
            capture_output=True,
            text=True,
            timeout=AUTH_STATUS_TIMEOUT_SECONDS,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    status = f"{result.stdout}\n{result.stderr}".casefold()
    if result.returncode != 0 or "not logged" in status or "logged out" in status:
        return "`codex` CLI is not authenticated; run `codex login`"
    return None


def runtime_inventory(skill_dir: Path) -> dict[str, bytes]:
    """Return only files a runtime may expose after selecting the skill."""
    inventory: dict[str, bytes] = {}
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return inventory
    inventory["SKILL.md"] = skill_md.read_bytes()
    for directory in RUNTIME_RESOURCE_DIRS:
        resource_dir = skill_dir / directory
        if not resource_dir.is_dir():
            continue
        for path in sorted(resource_dir.rglob("*")):
            if not path.is_file() or path.suffix == ".pyc" or "__pycache__" in path.parts:
                continue
            inventory[str(path.relative_to(skill_dir))] = path.read_bytes()
    return inventory


def matching_installed_skill(
    skill: str,
    installed_roots: list[Path],
) -> tuple[Path | None, list[Path]]:
    source_inventory = runtime_inventory(SKILLS / skill)
    candidates = [root.expanduser() / skill for root in installed_roots]
    for candidate in candidates:
        if runtime_inventory(candidate) == source_inventory:
            return candidate, candidates
    return None, candidates


def parse_case_specs(specs: list[str], skills: dict[str, str]) -> list[dict]:
    cases: list[dict] = []
    for spec in specs:
        name, separator, raw_id = spec.rpartition(":")
        if not separator or name not in skills or not raw_id.isdigit():
            raise ValueError(f"invalid --case {spec!r}; expected <skill-name>:<eval-id>")
        selected = trigger.load_cases(skills, [name], [int(raw_id)], None)
        if not selected:
            raise ValueError(f"eval case not found: {spec}")
        cases.extend(selected)
    return cases


def run_process(command: list[str], cwd: str) -> subprocess.CompletedProcess[str] | None:
    """Run Codex with a timeout that also terminates descendants holding its pipes."""
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        stdin=subprocess.DEVNULL,
        start_new_session=os.name == "posix",
    )
    try:
        stdout, stderr = process.communicate(timeout=CODEX_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.communicate()
        return None
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def run_codex(prompt: str, model: str | None = None) -> dict[str, object]:
    """Run one real, read-only Codex turn and return loaded skills and final text."""
    try:
        with tempfile.TemporaryDirectory(prefix="codex-catalog-eval-") as sandbox:
            command = [
                "codex",
                "exec",
                "--ephemeral",
                "--json",
                "--sandbox",
                "read-only",
                "--skip-git-repo-check",
                "--cd",
                sandbox,
            ]
            if model:
                command.extend(["--model", model])
            command.append(prompt)
            result = run_process(command, sandbox)
    except OSError as exc:
        return {"error": f"cannot start codex: {exc}", "loaded": [], "response": None}
    if result is None:
        return {"error": "codex-timeout", "loaded": [], "response": None}
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        return {
            "error": f"codex-exit-{result.returncode}: {detail[:240]}",
            "loaded": [],
            "response": None,
        }

    loaded: list[str] = []
    responses: list[str] = []
    event_error: str | None = None
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") in {"error", "turn.failed"}:
            event_error = str(event)[:240]
        item = event.get("item") or {}
        if event.get("type") != "item.completed":
            continue
        if item.get("type") == "command_execution":
            for name in SKILL_PATH_PATTERN.findall(item.get("command", "")):
                if name not in loaded:
                    loaded.append(name)
        elif item.get("type") == "agent_message":
            responses.append(item.get("text", ""))
    return {
        "error": event_error,
        "loaded": loaded,
        "response": responses[-1] if responses else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        metavar="SKILL:ID",
        help="run this eval case (repeatable)",
    )
    parser.add_argument("--skill", action="append", default=[], help="only this skill")
    parser.add_argument("--ids", type=int, nargs="+", default=[], help="eval ids with --skill")
    parser.add_argument("--limit", type=int, default=None, help="max cases per selected skill")
    parser.add_argument("--model", help="Codex model override; default uses the active profile")
    parser.add_argument("--runs-per-query", type=int, default=1, help="repeat each route N times")
    parser.add_argument(
        "--trigger-threshold",
        type=float,
        default=0.5,
        help="pass when the expected route holds in this fraction of runs",
    )
    parser.add_argument(
        "--installed-root",
        action="append",
        type=Path,
        default=[],
        help="root containing installed skill folders (repeatable)",
    )
    parser.add_argument(
        "--show-responses",
        action="store_true",
        help=(
            "print final answers for manual review; use only with self-contained "
            "evals whose inputs and possible ambient findings are safe to display"
        ),
    )
    args = parser.parse_args()

    if shutil.which("codex") is None:
        print("error: `codex` CLI not found on PATH", file=sys.stderr)
        return 1
    skills = trigger.load_skills()
    unknown = set(args.skill) - set(skills)
    if unknown:
        print(f"error: unknown skill(s): {', '.join(sorted(unknown))}", file=sys.stderr)
        return 1
    try:
        cases = (
            parse_case_specs(args.case, skills)
            if args.case
            else trigger.load_cases(skills, args.skill, args.ids, args.limit)
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not cases:
        print("error: no eval cases selected", file=sys.stderr)
        return 1

    installed_roots = args.installed_root or [
        Path("~/.codex/skills"),
        Path("~/.agents/skills"),
    ]
    for skill in sorted({case["skill"] for case in cases}):
        matched, candidates = matching_installed_skill(skill, installed_roots)
        if matched is None:
            locations = ", ".join(str(path.expanduser()) for path in candidates)
            print(
                f"error: no installed {skill} package matches the maintained source; checked {locations}",
                file=sys.stderr,
            )
            return 1
        print(
            f"source match: {skill} -> {matched.expanduser().resolve()}",
            file=sys.stderr,
            flush=True,
        )

    auth_problem = codex_auth_problem()
    if auth_problem:
        print(f"error: {auth_problem}", file=sys.stderr)
        return 1

    failures = 0
    unmeasured = 0
    runs = max(1, args.runs_per_query)
    for case in cases:
        results = []
        for run_index in range(1, runs + 1):
            print(
                f"RUN {case['skill']}#{case['id']} {run_index}/{runs}",
                file=sys.stderr,
                flush=True,
            )
            results.append(run_codex(case["prompt"], args.model))
        measured = [result for result in results if not result["error"]]
        if not measured:
            unmeasured += 1
            print(f"SKIP {case['skill']}#{case['id']}: all {runs} run(s) errored")
            continue
        holding = 0
        loaded_sets: list[str] = []
        for result in measured:
            loaded = set(result["loaded"])
            holds = case["skill"] not in loaded if case["negative"] else case["skill"] in loaded
            holding += int(holds)
            loaded_sets.append(",".join(result["loaded"]) or "none")
        rate = holding / len(measured)
        passed = rate >= args.trigger_threshold
        failures += int(not passed)
        expectation = f"NOT {case['skill']}" if case["negative"] else case["skill"]
        if runs == 1:
            detail = loaded_sets[0]
        else:
            low, high = trigger.wilson_interval(holding, len(measured))
            detail = f"rate={rate:.2f} CI[{low:.2f},{high:.2f}] loaded={';'.join(loaded_sets)}"
        print(
            f"{'PASS' if passed else 'FAIL'} {case['skill']}#{case['id']} "
            f"expected={expectation} loaded={detail}",
            flush=True,
        )
        if args.show_responses:
            payload = json.loads(
                (SKILLS / case["skill"] / "evals" / "evals.json").read_text(encoding="utf-8")
            )
            expected = next(
                item["expected_output"] for item in payload["evals"] if item["id"] == case["id"]
            )
            print(f"--- {case['skill']}#{case['id']} expected behavior ---")
            print(expected)
            for index, result in enumerate(measured, 1):
                print(f"--- {case['skill']}#{case['id']} run {index} response ---")
                print(result["response"] or "<no final response>")

    print("---")
    measured_total = len(cases) - unmeasured
    print(
        f"total: {measured_total - failures}/{measured_total} "
        f"routing expectations passed ({unmeasured} unmeasured)"
    )
    if args.show_responses:
        print(
            "note: routing is automated; final-answer quality requires manual transcript review"
        )
    return 1 if failures or unmeasured else 0


if __name__ == "__main__":
    raise SystemExit(main())
