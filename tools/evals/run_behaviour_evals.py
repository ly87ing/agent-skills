#!/usr/bin/env python3
"""Measure whether a skill changes what the model DOES, not just when it loads.

run_trigger_evals.py answers "would the agent pick this skill?". It cannot answer
the question the official guidance puts first: would the agent have got this right
anyway? A clause that the model already honours without being told is dead weight
that every trigger pays for, and no amount of trigger-passing reveals it.

Each case is run twice against the same request — once with the skill body and its
runtime resources available, and once without — and a separate judge call grades
each answer against the case's expected_output. Three numbers matter:

  with    — how often the skill-loaded answer satisfies the expectation
  without — how often the bare model satisfies it anyway
  lift    — with minus without, the only figure that justifies the clause

A case where `without` already passes is not a success. It is the delete test
firing: that expectation needed no skill, so whatever clause it covers should be
re-examined and, absent another reason, cut.

For an existing-skill optimization, compare against the pre-edit skill rather than
against no skill: unpack or check out the previous catalog in a separate directory
and pass it with `--baseline-root`. Both current and baseline arms then receive the
same runtime-only resource treatment. Keep the no-skill control for new skills and
for testing whether a clause is redundant.

Grading is a model call and therefore noisy in exactly the way documented in
run_trigger_evals.py — read the Wilson interval, not the point rate, and do not
compare a number here against one measured in an earlier run.

Use `--show-responses` to inspect both arms when diagnosing a score. It prints the
model answers to stdout and should therefore be used only when the eval input is
safe to display; the runner never writes transcripts to the repository.

Before loosening the grader, read the response yourself and find the missing point.
The first FAIL this runner produced looked obviously wrong: the answer diagnosed the
ignore-rule trap, said to re-search with ignore rules off, and said to confirm the
file entered the commit — so a looser grader prompt was drafted to accept it. Reading
the expectation again showed the grader was right and the draft was wrong: the answer
never said to run `git add -f` or fix the rule, so it verified the problem without
ever fixing it. A grader tuned until it agrees with you measures nothing. Loosen it
only for a difference in wording or an equivalent command, never for a missing step.

Read `with 0/N without 0/N` as "measured nothing", never as the delete test firing.
The delete test needs `without` to PASS; a case where BOTH arms fail says the harness
could not put the model in a position to answer, and the commonest cause is a prompt
that names material it does not carry ("our repo's AGENTS.md", "this iteration's
to-do items", "这页状态汇报"). `claude -p` is a full agent with file tools: it goes
looking for that material, and a real reading of one such response had it locate an
unrelated `AGENTS.md` under the working directory and answer that the file did not
match the description — never performing the task, so both arms fail identically.
Both answer arms therefore start in fresh temporary directories. The no-skill arm
is empty; the skill arm contains only the selected skill's runtime files. This makes
the failure honest rather than random, but does not by itself make such a case
measurable. To measure one, give it a `behaviour_prompt`: the same request with the
material inlined, which only this runner reads, leaving `prompt` free to stay the
way a user really opens the request for run_trigger_evals.py. Editing `prompt`
itself to fix behaviour measurement would silently move the trigger reading too.
Cases whose expectation is about method rather than a produced artifact (compress
this, rewrite with no tone given) do not have this problem.

A second reason both arms can fail: an expectation that is a conjunction of four or
five clauses fails on any single missed clause, so it measures the model's coverage
of a checklist rather than the skill's effect. Split such a case, or read the
response before believing the verdict.

Every answer and grading call disables ambient Claude customizations, slash-command
skills, MCP servers, and session persistence. The skill arm gets a whitelist copy of
`SKILL.md`, `references/`, `scripts/`, and `assets/`; it never receives `evals/`,
tests, agent metadata, or the expected answer. Answer calls get read-only file tools
so referenced guidance can load on demand. This harness does not execute bundled
scripts; deterministic script behavior belongs in the per-skill unit suites.

Usage:
  python3 tools/evals/run_behaviour_evals.py --skill change-discipline --ids 23 24 25
  python3 tools/evals/run_behaviour_evals.py --skill safe-merge-review --runs-per-case 3
  python3 tools/evals/run_behaviour_evals.py --skill safe-merge-review --baseline-root /tmp/previous-catalog

Cost: 4 model calls per case per run (two answers, then one grade each). Start narrow.
Exit code: 0 when every selected case shows positive lift, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ANSWER_TIMEOUT_SECONDS = 300
GRADE_TIMEOUT_SECONDS = 180
AUTH_STATUS_TIMEOUT_SECONDS = 10

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


RUNTIME_RESOURCE_DIRS = ("assets", "references", "scripts")
READ_ONLY_TOOLS = "Read,Glob,Grep"
CLAUDE_ISOLATION_ARGS = (
    "--safe-mode",
    "--disable-slash-commands",
    "--no-session-persistence",
    "--strict-mcp-config",
)


def claude_auth_problem() -> str | None:
    """Return a recovery message only when the CLI explicitly reports logged out."""
    try:
        result = subprocess.run(
            ["claude", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=AUTH_STATUS_TIMEOUT_SECONDS,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    try:
        status = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if status.get("loggedIn") is False:
        return "`claude` CLI is not authenticated; run `claude auth login`"
    return None

def run_claude(
    prompt: str,
    model: str,
    timeout: int,
    cwd: str,
    tools: str = READ_ONLY_TOOLS,
) -> str | None:
    try:
        result = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--model",
                model,
                *CLAUDE_ISOLATION_ARGS,
                "--tools",
                tools,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            cwd=cwd,
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


def skill_body(skill: str, source_root: Path = ROOT) -> str:
    text = (source_root / skill / "SKILL.md").read_text(encoding="utf-8")
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL).strip()


def materialize_runtime_skill(
    skill: str,
    destination: Path,
    source_root: Path = ROOT,
) -> Path:
    """Copy only files a real skill may expose after activation."""
    source = source_root / skill
    source_skill = source / "SKILL.md"
    if source_skill.is_symlink():
        raise ValueError(f"refusing runtime SKILL.md symlink: {skill}")
    runtime_skill = destination / skill
    runtime_skill.mkdir(parents=True)
    shutil.copy2(source_skill, runtime_skill / "SKILL.md")
    for directory in RUNTIME_RESOURCE_DIRS:
        source_directory = source / directory
        if not source_directory.is_dir():
            continue
        symlinks = [path for path in source_directory.rglob("*") if path.is_symlink()]
        if symlinks:
            relative = symlinks[0].relative_to(source)
            raise ValueError(f"refusing runtime resource symlink: {skill}/{relative}")
        shutil.copytree(source_directory, runtime_skill / directory)
    return runtime_skill


def loaded_skill_prompt(body: str, runtime_skill: Path, asked: str) -> str:
    return (
        "The following skill has already been selected for this request. Follow its "
        "instructions. Bundled references, scripts, and assets are available under "
        f"{runtime_skill}; read a referenced file there when the instructions require it.\n\n"
        f"<skill_instructions>\n{body}\n</skill_instructions>\n\n"
        f"<user_request>\n{asked}\n</user_request>"
    )


def answer_once(
    skill: str,
    body: str,
    asked: str,
    model: str,
    baseline_root: Path | None = None,
) -> dict[str, str | None]:
    """Run one treatment/control pair without sharing files or session state."""
    with tempfile.TemporaryDirectory(prefix="behaviour-eval-with-") as with_cwd:
        runtime_skill = materialize_runtime_skill(skill, Path(with_cwd))
        with_answer = run_claude(
            loaded_skill_prompt(body, runtime_skill, asked),
            model,
            ANSWER_TIMEOUT_SECONDS,
            cwd=with_cwd,
        )
    if baseline_root is None:
        with tempfile.TemporaryDirectory(prefix="behaviour-eval-without-") as without_cwd:
            without_answer = run_claude(
                asked,
                model,
                ANSWER_TIMEOUT_SECONDS,
                cwd=without_cwd,
            )
    else:
        with tempfile.TemporaryDirectory(prefix="behaviour-eval-baseline-") as baseline_cwd:
            baseline_skill = materialize_runtime_skill(
                skill,
                Path(baseline_cwd),
                source_root=baseline_root,
            )
            without_answer = run_claude(
                loaded_skill_prompt(
                    skill_body(skill, source_root=baseline_root),
                    baseline_skill,
                    asked,
                ),
                model,
                ANSWER_TIMEOUT_SECONDS,
                cwd=baseline_cwd,
            )
    return {"with": with_answer, "without": without_answer}


def grade(prompt: str, expectation: str, response: str | None, model: str) -> bool | None:
    if response is None:
        return None
    with tempfile.TemporaryDirectory(prefix="behaviour-eval-grade-") as grader_cwd:
        verdict = run_claude(
            GRADE_TEMPLATE.format(prompt=prompt, expectation=expectation, response=response),
            model,
            GRADE_TIMEOUT_SECONDS,
            cwd=grader_cwd,
            tools="",
        )
    if verdict is None:
        return None
    head = verdict.strip().upper()
    if "PASS" in head and "FAIL" not in head:
        return True
    if "FAIL" in head:
        return False
    return None


def answered_prompt(case: dict) -> str:
    """The prompt both arms actually answer.

    A case's `prompt` is written the way a user opens the request, because that is
    what run_trigger_evals.py measures — and real openings routinely name material
    they do not carry ("this iteration's to-do items", "这两段"). That is correct
    for triggering and fatal for behaviour: both arms go looking for material that
    is not there and fail identically, printing `with 0/N without 0/N`, which
    measures nothing. `behaviour_prompt` restates the same request with the
    material inlined, so one case can serve both harnesses without one prompt
    having to serve both jobs. Cases that carry their own material need only
    `prompt`.
    """
    return case.get("behaviour_prompt") or case["prompt"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, help="skill whose behaviour to measure")
    parser.add_argument("--ids", type=int, nargs="+", default=[], help="only these eval ids")
    parser.add_argument("--runs-per-case", type=int, default=1, help="repeat each case N times (default: 1)")
    parser.add_argument("--model", default="sonnet", help="model under test and grader (default: sonnet)")
    parser.add_argument(
        "--baseline-root",
        type=Path,
        help="previous catalog root; compare against its copy of the skill instead of no skill",
    )
    parser.add_argument(
        "--show-responses",
        action="store_true",
        help="print both model answers for manual review; use only with non-sensitive eval inputs",
    )
    args = parser.parse_args()

    if shutil.which("claude") is None:
        print("error: `claude` CLI not found on PATH; install/login Claude Code first", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.skill):
        print(f"error: invalid skill name: {args.skill}", file=sys.stderr)
        return 1
    if not (ROOT / args.skill / "SKILL.md").is_file():
        print(f"error: no such skill: {args.skill}", file=sys.stderr)
        return 1

    baseline_root = args.baseline_root.resolve() if args.baseline_root else None
    if baseline_root is not None and not (baseline_root / args.skill / "SKILL.md").is_file():
        print(
            f"error: baseline has no {args.skill}/SKILL.md: {baseline_root}",
            file=sys.stderr,
        )
        return 1

    cases = load_cases(args.skill, args.ids)
    if not cases:
        print("error: no positive eval cases selected", file=sys.stderr)
        return 1
    auth_problem = claude_auth_problem()
    if auth_problem:
        print(f"error: {auth_problem}", file=sys.stderr)
        return 1

    body = skill_body(args.skill)
    runs = max(1, args.runs_per_case)
    ungraded = 0
    totals = {"with": 0, "without": 0, "n": 0}
    all_cases_positive = True
    labels = {
        "with": "current" if baseline_root else "with",
        "without": "baseline" if baseline_root else "without",
    }

    for case in cases:
        scores = {"with": 0, "without": 0, "n": 0}
        asked = answered_prompt(case)
        for run_index in range(1, runs + 1):
            answers = answer_once(
                args.skill,
                body,
                asked,
                args.model,
                baseline_root=baseline_root,
            )
            if args.show_responses:
                for arm in ("with", "without"):
                    print(f"--- #{case['id']} run {run_index} {labels[arm]} response ---")
                    print(answers[arm] if answers[arm] is not None else "<no response>")
            verdicts = {
                arm: grade(asked, case["expected_output"], answers[arm], args.model)
                for arm in ("with", "without")
            }
            if None in verdicts.values():
                ungraded += 1
                continue
            scores["n"] += 1
            for arm in ("with", "without"):
                scores[arm] += int(verdicts[arm] is True)
        if scores["n"] == 0:
            all_cases_positive = False
            print(f"#{case['id']}: no graded runs")
            continue
        lift = (scores["with"] - scores["without"]) / scores["n"]
        if lift <= 0:
            all_cases_positive = False
        if lift > 0:
            verdict = "improves baseline" if baseline_root else "earns it"
        elif baseline_root:
            verdict = "no improvement over baseline"
        elif scores["without"] == scores["n"]:
            verdict = "DELETE TEST: bare model already passes"
        else:
            verdict = "no lift"
        print(
            f"#{case['id']}: {labels['with']} {scores['with']}/{scores['n']} "
            f"{labels['without']} {scores['without']}/{scores['n']} "
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
        print(
            f"{labels[arm]:8}: {totals[arm]}/{totals['n']} = "
            f"{totals[arm]/totals['n']:.2f} CI[{low:.2f},{high:.2f}]"
        )
    lift = (totals["with"] - totals["without"]) / totals["n"]
    print(f"lift    : {lift:+.2f} (model={args.model}, runs={runs})")
    if ungraded:
        print(f"note: {ungraded} run(s) could not be graded and were dropped")
    with_low, _ = wilson_interval(totals["with"], totals["n"])
    _, without_high = wilson_interval(totals["without"], totals["n"])
    if with_low <= without_high:
        print("note: the two intervals overlap — this N does not establish that the skill changed anything")
    return 0 if all_cases_positive else 1


if __name__ == "__main__":
    sys.exit(main())
