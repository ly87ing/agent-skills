#!/usr/bin/env python3
"""Judge skill-triggering decisions in evals.json against a live model.

For each eval case, the judge model is shown all maintained skills'
name + description pairs — exactly the metadata an agent sees before loading
any skill body — plus the eval prompt, and asked which single skill it would
load. A positive case (expected_output starting "Should trigger") passes when
the judge picks this skill; a negative case ("Should not/NOT ...") passes
when the judge picks anything else, including none.

Requires the `claude` CLI, logged in. The judge prompt is self-contained,
but `claude -p` still loads user-level CLAUDE.md, so treat results as a
realistic triggering signal for this machine, not a hermetic benchmark.

Usage:
  python3 tests/run_trigger_evals.py                        # all skills
  python3 tests/run_trigger_evals.py --skill safe-merge-review --ids 12 13
  python3 tests/run_trigger_evals.py --model sonnet --jobs 4
  python3 tests/run_trigger_evals.py --limit 2              # 2 cases per skill
  python3 tests/run_trigger_evals.py --runs-per-query 3     # decide by rate, not one sample

A single run per case cannot tell a real failure from noise: borderline cases
flip between runs. Judge a case more than once (`--runs-per-query 3`) and it
passes when the expectation holds in at least `--trigger-threshold` of them.

Known limit — do not decide a borderline case from one batch. Measured on
2026-07-19 against one case sitting near the boundary: 12 serial judgements
gave a 0.17 rate, 12 concurrent ones (--jobs 6) gave 0.42, and separate small
batches of the identical configuration earlier returned 1.00. Sampling alone
cannot produce that spread, so the rate itself drifts between batches; --jobs
appears to shift it further, though 12-vs-12 is too small to prove causation.
Practical rule: compare candidates inside ONE batch under identical settings,
never against a number measured earlier; when the effect you are chasing is
smaller than this spread, the instrument cannot settle it — say so instead of
shipping a change the numbers appear to justify.

Run with --model haiku/sonnet/opus in turn to cover the official
"test with all models you plan to use" checklist item.
Exit code: 0 when every selected case passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# claude -p pays CLI startup plus model latency per call; generous headroom
# so cold starts never flake a run.
JUDGE_TIMEOUT_SECONDS = 180

NEGATIVE_EXPECTATION = re.compile(r"^\s*should\s+not\b", re.IGNORECASE)

JUDGE_TEMPLATE = """You simulate the skill-selection step of an AI coding agent.
The agent sees only these skill names and descriptions:

{catalog}

User request:
<<<
{prompt}
>>>

Which single skill, if any, should the agent load for this request?
Answer with exactly one skill name from the list above, or the word none. Output only that answer.
"""


def load_skills() -> dict[str, str]:
    skills: dict[str, str] = {}
    for skill_dir in sorted(ROOT.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.exists():
            continue
        match = re.match(r"^---\n(.*?)\n---", skill_md.read_text(encoding="utf-8"), re.DOTALL)
        if not match:
            raise SystemExit(f"error: frontmatter missing in {skill_md}")
        frontmatter = dict(
            (key.strip(), value.strip().strip('"'))
            for key, value in (line.split(":", 1) for line in match.group(1).splitlines())
        )
        skills[frontmatter["name"]] = frontmatter["description"]
    return skills


def load_cases(skills: dict[str, str], only_skills: list[str], ids: list[int], limit: int | None):
    cases = []
    for name in skills:
        if only_skills and name not in only_skills:
            continue
        payload = json.loads((ROOT / name / "evals" / "evals.json").read_text(encoding="utf-8"))
        selected = [case for case in payload["evals"] if not ids or case["id"] in ids]
        if limit is not None:
            selected = selected[:limit]
        for case in selected:
            cases.append(
                {
                    "skill": name,
                    "id": case["id"],
                    "prompt": case["prompt"],
                    "negative": bool(NEGATIVE_EXPECTATION.match(case["expected_output"])),
                }
            )
    return cases


def judge(catalog: str, skills: dict[str, str], model: str, case: dict) -> str:
    prompt = JUDGE_TEMPLATE.format(catalog=catalog, prompt=case["prompt"])
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model],
            capture_output=True,
            text=True,
            timeout=JUDGE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return "error:judge-timeout"
    if result.returncode != 0:
        return f"error:claude-exit-{result.returncode}:{result.stderr.strip()[:120]}"
    answer = result.stdout.strip().lower()
    mentioned = {name for name in skills if re.search(rf"\b{re.escape(name)}\b", answer)}
    if len(mentioned) == 1:
        return mentioned.pop()
    if len(mentioned) > 1:
        return f"error:ambiguous:{answer[:120]}"
    if re.search(r"\bnone\b", answer):
        return "none"
    # The judge answered but named nothing from the catalog (e.g. a skill it
    # wishes existed). That is a definite "not any of these": passes a
    # negative case, fails a positive one — unlike error:* which fails both.
    return f"other:{answer[:120]}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", action="append", default=[], help="only this skill (repeatable)")
    parser.add_argument("--ids", type=int, nargs="+", default=[], help="only these eval ids")
    parser.add_argument("--limit", type=int, default=None, help="max cases per skill")
    parser.add_argument("--model", default="haiku", help="judge model passed to claude -p (default: haiku)")
    parser.add_argument("--jobs", type=int, default=1, help="concurrent judge calls (default: 1)")
    parser.add_argument(
        "--runs-per-query",
        type=int,
        default=1,
        help="judge each case N times and decide by rate (default: 1); borderline cases flip between runs",
    )
    parser.add_argument(
        "--trigger-threshold",
        type=float,
        default=0.5,
        help="pass when the expectation holds in at least this fraction of runs (default: 0.5)",
    )
    args = parser.parse_args()

    if shutil.which("claude") is None:
        print("error: `claude` CLI not found on PATH; install/login Claude Code first", file=sys.stderr)
        return 1

    skills = load_skills()
    unknown = set(args.skill) - set(skills)
    if unknown:
        print(f"error: unknown skill(s): {', '.join(sorted(unknown))}", file=sys.stderr)
        return 1
    catalog = "\n".join(f"- {name}: {description}" for name, description in skills.items())
    cases = load_cases(skills, args.skill, args.ids, args.limit)
    if not cases:
        print("error: no eval cases selected", file=sys.stderr)
        return 1

    runs = max(1, args.runs_per_query)
    trials = [case for case in cases for _ in range(runs)]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        trial_verdicts = list(pool.map(lambda case: judge(catalog, skills, args.model, case), trials))
    verdicts = [trial_verdicts[index * runs : (index + 1) * runs] for index in range(len(cases))]

    def holds(case: dict, judged: str) -> bool:
        if judged.startswith("error:"):
            return False
        return judged != case["skill"] if case["negative"] else judged == case["skill"]

    failures = 0
    per_skill: dict[str, list[int]] = {}
    for case, judged_runs in zip(cases, verdicts):
        rate = sum(holds(case, judged) for judged in judged_runs) / runs
        passed = rate >= args.trigger_threshold
        judged = judged_runs[0] if runs == 1 else f"rate={rate:.2f} {','.join(sorted(set(judged_runs)))}"
        stats = per_skill.setdefault(case["skill"], [0, 0])
        stats[1] += 1
        if passed:
            stats[0] += 1
        else:
            failures += 1
        expectation = f"NOT {case['skill']}" if case["negative"] else case["skill"]
        print(f"{'PASS' if passed else 'FAIL'} {case['skill']}#{case['id']} expected={expectation} judged={judged}")

    print("---")
    if failures and runs == 1:
        print("note: one run cannot separate a real failure from noise — re-check each failure with --runs-per-query 3")
    for name, (passed_count, total) in sorted(per_skill.items()):
        print(f"{name}: {passed_count}/{total}")
    print(f"total: {len(cases) - failures}/{len(cases)} passed (model={args.model}, runs={runs})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
