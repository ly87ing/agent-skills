#!/usr/bin/env python3
"""Measure whether a skill changes what the model DOES, not just when it loads.

run_trigger_evals.py answers "would the agent pick this skill?". It cannot answer
the question the official guidance puts first: would the agent have got this right
anyway? A clause that the model already honours without being told is dead weight
that every trigger pays for, and no amount of trigger-passing reveals it.

Each case is run twice against the same prompt — once with the skill body prepended
and once without — and a separate judge call grades each answer against the case's
expected_output. Three numbers matter:

  with    — how often the skill-loaded answer satisfies the expectation
  without — how often the bare model satisfies it anyway
  lift    — with minus without, the only figure that justifies the clause

A case where `without` already passes is not a success. It is the delete test
firing: that expectation needed no skill, so whatever clause it covers should be
re-examined and, absent another reason, cut.

Grading is a model call and therefore noisy in exactly the way documented in
run_trigger_evals.py — read the Wilson interval, not the point rate, and do not
compare a number here against one measured in an earlier run.

Before loosening the grader, read the response yourself and find the missing point.
The first FAIL this runner produced looked obviously wrong: the answer diagnosed the
ignore-rule trap, said to re-search with ignore rules off, and said to confirm the
file entered the commit — so a looser grader prompt was drafted to accept it. Reading
the expectation again showed the grader was right and the draft was wrong: the answer
never said to run `git add -f` or fix the rule, so it verified the problem without
ever fixing it. A grader tuned until it agrees with you measures nothing. Loosen it
only for a difference in wording or an equivalent command, never for a missing step.

Known limit — this runner prepends SKILL.md's body and nothing else, so a rule that
lives in `references/` is absent from the with-skill arm even though a real agent
would load it on demand. Any case whose expectation rests on a bundled reference
reads as a regression here that the runtime does not have. Judge such a case by
reading the response for whether it went looking for the reference, or measure it
in a runtime where the skill directory is actually installed.

Usage:
  python3 tests/run_behaviour_evals.py --skill change-discipline --ids 23 24 25
  python3 tests/run_behaviour_evals.py --skill safe-merge-review --runs-per-case 3

Cost: 3 model calls per case per run (with, without, grade). Start narrow.
Exit code: 0 when every selected case shows positive lift, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ANSWER_TIMEOUT_SECONDS = 300
GRADE_TIMEOUT_SECONDS = 180

NEGATIVE_EXPECTATION = re.compile(r"^\s*should\s+not\b", re.IGNORECASE)

GRADE_TEMPLATE = """You are grading whether a response satisfies a stated expectation.

The user's request was:
<<<REQUEST
{prompt}
REQUEST

The expectation the response must satisfy:
<<<EXPECTATION
{expectation}
EXPECTATION

The response to grade:
<<<RESPONSE
{response}
RESPONSE

Ignore whether the response mentions any skill by name, and ignore tone, length and
formatting. Grade only whether the response's substance does what the expectation
requires. Judge only what the response actually says: do not credit it for a point
it merely gestures at, and do not penalise extra correct material.

Answer with exactly one word: PASS or FAIL.
"""


def run_claude(prompt: str, model: str, timeout: int) -> str | None:
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def wilson_interval(passes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (0.0, 1.0)
    rate = passes / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    spread = z * ((rate * (1 - rate) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return (max(0.0, center - spread), min(1.0, center + spread))


def load_cases(skill: str, ids: list[int]) -> list[dict]:
    payload = json.loads((ROOT / skill / "evals" / "evals.json").read_text(encoding="utf-8"))
    cases = [case for case in payload["evals"] if not ids or case["id"] in ids]
    # A negative case asserts the skill should not load at all, so there is no
    # behaviour of this skill to measure — trigger evals already cover those.
    return [case for case in cases if not NEGATIVE_EXPECTATION.match(case["expected_output"])]


def skill_body(skill: str) -> str:
    text = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL).strip()


def grade(prompt: str, expectation: str, response: str | None, model: str) -> bool | None:
    if response is None:
        return None
    verdict = run_claude(
        GRADE_TEMPLATE.format(prompt=prompt, expectation=expectation, response=response),
        model,
        GRADE_TIMEOUT_SECONDS,
    )
    if verdict is None:
        return None
    head = verdict.strip().upper()
    if "PASS" in head and "FAIL" not in head:
        return True
    if "FAIL" in head:
        return False
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, help="skill whose behaviour to measure")
    parser.add_argument("--ids", type=int, nargs="+", default=[], help="only these eval ids")
    parser.add_argument("--runs-per-case", type=int, default=1, help="repeat each case N times (default: 1)")
    parser.add_argument("--model", default="sonnet", help="model under test and grader (default: sonnet)")
    args = parser.parse_args()

    if shutil.which("claude") is None:
        print("error: `claude` CLI not found on PATH; install/login Claude Code first", file=sys.stderr)
        return 1
    if not (ROOT / args.skill / "SKILL.md").exists():
        print(f"error: no such skill: {args.skill}", file=sys.stderr)
        return 1

    cases = load_cases(args.skill, args.ids)
    if not cases:
        print("error: no positive eval cases selected", file=sys.stderr)
        return 1

    body = skill_body(args.skill)
    runs = max(1, args.runs_per_case)
    ungraded = 0
    totals = {"with": 0, "without": 0, "n": 0}

    for case in cases:
        scores = {"with": 0, "without": 0, "n": 0}
        for _ in range(runs):
            answers = {
                "with": run_claude(f"{body}\n\n---\n\n{case['prompt']}", args.model, ANSWER_TIMEOUT_SECONDS),
                "without": run_claude(case["prompt"], args.model, ANSWER_TIMEOUT_SECONDS),
            }
            verdicts = {
                arm: grade(case["prompt"], case["expected_output"], answers[arm], args.model)
                for arm in ("with", "without")
            }
            if None in verdicts.values():
                ungraded += 1
                continue
            scores["n"] += 1
            for arm in ("with", "without"):
                scores[arm] += verdicts[arm]
        if scores["n"] == 0:
            print(f"#{case['id']}: no graded runs")
            continue
        lift = (scores["with"] - scores["without"]) / scores["n"]
        verdict = "earns it" if lift > 0 else ("DELETE TEST: bare model already passes" if scores["without"] == scores["n"] else "no lift")
        print(
            f"#{case['id']}: with {scores['with']}/{scores['n']} without {scores['without']}/{scores['n']} "
            f"lift {lift:+.2f} — {verdict}"
        )
        for arm in ("with", "without"):
            totals[arm] += scores[arm]
        totals["n"] += scores["n"]

    if totals["n"] == 0:
        print("no graded runs at all", file=sys.stderr)
        return 1
    print("---")
    for arm in ("with", "without"):
        low, high = wilson_interval(totals[arm], totals["n"])
        print(f"{arm:8}: {totals[arm]}/{totals['n']} = {totals[arm]/totals['n']:.2f} CI[{low:.2f},{high:.2f}]")
    lift = (totals["with"] - totals["without"]) / totals["n"]
    print(f"lift    : {lift:+.2f} (model={args.model}, runs={runs})")
    if ungraded:
        print(f"note: {ungraded} run(s) could not be graded and were dropped")
    with_low, _ = wilson_interval(totals["with"], totals["n"])
    _, without_high = wilson_interval(totals["without"], totals["n"])
    if with_low <= without_high:
        print("note: the two intervals overlap — this N does not establish that the skill changed anything")
    return 0 if lift > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
