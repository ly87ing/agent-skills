#!/usr/bin/env python3
"""Judge skill-triggering decisions in evals.json against a live model.

For each eval case, the judge model is shown all maintained skills'
name + description pairs — exactly the metadata an agent sees before loading
any skill body — plus the eval prompt, and asked which single skill it would
load. A positive case (expected_output starting "Should trigger") passes when
the judge picks this skill; a negative case ("Should not/NOT ...") passes
when the judge picks anything else, including none.

Requires the `claude` CLI, logged in. Every judge call starts in a fresh empty
directory with ambient Claude customizations, slash-command skills, MCP servers,
tools, and session persistence disabled. The catalog and request in the judge
prompt are therefore the only task-specific context.

Usage:
  python3 tools/evals/run_trigger_evals.py                        # all skills
  python3 tools/evals/run_trigger_evals.py --skill safe-merge-review --ids 12 13
  python3 tools/evals/run_trigger_evals.py --model sonnet --jobs 4
  python3 tools/evals/run_trigger_evals.py --limit 2              # 2 cases per skill
  python3 tools/evals/run_trigger_evals.py --runs-per-query 3     # decide by rate, not one sample

A single run per case cannot tell a real failure from noise: borderline cases
flip between runs. Judge a case more than once (`--runs-per-query 3`) and it
passes when the expectation holds in at least `--trigger-threshold` of them.

Known limit — a rate from a handful of runs is nearly uninformative, so the
report prints a Wilson 95% interval beside it and marks `?` when that interval
straddles the threshold. A `?` means this N decided nothing; it is not a pass.

Reading rates without their interval is the mistake this guards against. One
borderline case returned 0.17, 0.58 and 0.40 across three separate runs of the
IDENTICAL configuration on 2026-07-19, which looks like the instrument drifting
— but a chi-square homogeneity test over those runs gives p≈0.11: they are all
consistent with one true rate near 0.38, and the spread is ordinary binomial
noise at N≈10. Small N, not drift.

Concurrency is a real effect on top of that, though. Judging the same case with
--jobs 6 returned 1.00 where paired interleaved runs of the same description
gave 0.10, and a homogeneity test across that candidate's runs does reject
(p<0.001), driven entirely by the concurrent one. Judge serially when the
result has to carry a decision.

To compare two candidate descriptions, alternate them one judgement at a time
inside a single run (A, C, A, C ...), swapping which goes first — a block
design (all of A, then all of C) lets any time-varying effect land on the
candidate difference. Then compare intervals, not point rates: 13/34 versus
1/27 separates cleanly (non-overlapping intervals, Fisher p≈0.002), while the
same gap at N=5 per arm would not have been evidence of anything.

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
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"

# claude -p pays CLI startup plus model latency per call; generous headroom
# so cold starts never flake a run.
JUDGE_TIMEOUT_SECONDS = 180
AUTH_STATUS_TIMEOUT_SECONDS = 10
CLAUDE_ISOLATION_ARGS = (
    "--safe-mode",
    "--disable-slash-commands",
    "--no-session-persistence",
    "--strict-mcp-config",
)

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


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", skill_md.read_text(encoding="utf-8"), re.DOTALL)
    if not match:
        raise SystemExit(f"error: frontmatter missing in {skill_md}")
    return dict(
        (key.strip(), value.strip().strip('"'))
        for key, value in (line.split(":", 1) for line in match.group(1).splitlines())
    )


def load_neighbour_skills(catalog_dirs: list[str], own: set[str]) -> dict[str, str]:
    """Skills the agent can also choose from but this repo does not own.

    A real agent picks among every installed skill. A catalog of only the skills
    maintained here cannot surface the collisions that matter
    most — safe-merge-review against a GitLab skill, verification
    against a runtime's built-in dataviz skill — so measuring without them
    reads optimistically.
    """
    neighbours: dict[str, str] = {}
    for raw_dir in catalog_dirs:
        base = Path(raw_dir).expanduser()
        if not base.is_dir():
            raise SystemExit(f"error: catalog dir not found: {base}")
        for skill_dir in sorted(base.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            frontmatter = read_frontmatter(skill_md)
            name = frontmatter.get("name", skill_dir.name)
            if name in own or name in neighbours:
                continue
            neighbours[name] = frontmatter["description"]
    return neighbours


def load_skills() -> dict[str, str]:
    skills: dict[str, str] = {}
    for skill_dir in sorted(SKILLS.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.exists():
            continue
        frontmatter = read_frontmatter(skill_md)
        skills[frontmatter["name"]] = frontmatter["description"]
    return skills


def load_cases(skills: dict[str, str], only_skills: list[str], ids: list[int], limit: int | None):
    cases = []
    for name in skills:
        if only_skills and name not in only_skills:
            continue
        payload = json.loads((SKILLS / name / "evals" / "evals.json").read_text(encoding="utf-8"))
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
        with tempfile.TemporaryDirectory(prefix="trigger-eval-") as sandbox:
            result = subprocess.run(
                [
                    "claude",
                    "-p",
                    prompt,
                    "--model",
                    model,
                    *CLAUDE_ISOLATION_ARGS,
                    "--tools",
                    "",
                ],
                capture_output=True,
                text=True,
                timeout=JUDGE_TIMEOUT_SECONDS,
                stdin=subprocess.DEVNULL,
                cwd=sandbox,
            )
    except subprocess.TimeoutExpired:
        return "error:judge-timeout"
    if result.returncode != 0:
        return f"error:claude-exit-{result.returncode}:{result.stderr.strip()[:120]}"
    answer = result.stdout.strip().lower()
    # Skill names contain hyphens, so \b is the wrong boundary: it treats "-" as a
    # separator and lets a short neighbour name like "ones" match inside a longer
    # one like "ones-manhour-fill", making every
    # answer naming the longer skill look ambiguous. Exclude hyphens from the
    # boundary so only a whole skill name matches.
    mentioned = {
        name for name in skills if re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", answer)
    }
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


def wilson_interval(passes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval — usable at the small N these runs can afford,
    unlike the normal approximation, which degenerates at rates near 0 and 1."""
    if total == 0:
        return (0.0, 1.0)
    rate = passes / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    spread = z * ((rate * (1 - rate) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return (max(0.0, center - spread), min(1.0, center + spread))


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
        "--catalog-dir",
        action="append",
        default=[],
        metavar="DIR",
        help="also show the judge every SKILL.md under DIR (repeatable), e.g. ~/.claude/skills — "
        "our own skills alone are an optimistic catalog, since a real agent chooses among everything installed",
    )
    parser.add_argument(
        "--require-catalog-skill",
        action="append",
        default=[],
        metavar="NAME",
        help="fail before judging unless NAME is present in the assembled catalog (repeatable)",
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
    # Cases come from our own skills; the catalog the judge sees also carries the
    # neighbours, so a case can fail by losing to a skill this repo does not own.
    cases = load_cases(skills, args.skill, args.ids, args.limit)
    neighbours = load_neighbour_skills(args.catalog_dir, own=set(skills))
    missing_required = sorted(set(args.require_catalog_skill) - set(skills) - set(neighbours))
    if missing_required:
        print(
            "error: required catalog skill(s) missing: " + ", ".join(missing_required),
            file=sys.stderr,
        )
        return 1
    if neighbours:
        print(f"catalog: {len(skills)} own + {len(neighbours)} neighbour skills", file=sys.stderr)
        for raw_dir in args.catalog_dir:
            stamp = Path(raw_dir).expanduser() / "CAPTURED"
            if stamp.exists():
                print(f"  {Path(raw_dir).name}: {stamp.read_text(encoding='utf-8').strip()}", file=sys.stderr)
    else:
        # Silence here is how an optimistic run passes for a real one: a case scores
        # green because the neighbour that would have taken it was never shown, and
        # the output looks identical to a run that measured the whole catalog.
        print(
            f"WARNING: no --catalog-dir given — the judge chooses among these {len(skills)} "
            "skills alone, which is not the catalog any real agent faces. Runtime built-ins "
            "have no directory to read, so they are absent unless you supply them. Results "
            "from this catalog read optimistically and CANNOT establish a boundary: a green "
            "here may only mean the competing skill was missing. Pass "
            "--catalog-dir tools/evals/fixtures/builtin-skills (plus your runtime's own skill dirs) "
            "for any result you intend to act on.",
            file=sys.stderr,
        )
    skills = {**skills, **neighbours}
    catalog = "\n".join(f"- {name}: {description}" for name, description in skills.items())
    if not cases:
        print("error: no eval cases selected", file=sys.stderr)
        return 1
    auth_problem = claude_auth_problem()
    if auth_problem:
        print(f"error: {auth_problem}", file=sys.stderr)
        return 1

    runs = max(1, args.runs_per_query)
    trials = [case for case in cases for _ in range(runs)]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        trial_verdicts = list(pool.map(lambda case: judge(catalog, skills, args.model, case), trials))
    verdicts = [trial_verdicts[index * runs : (index + 1) * runs] for index in range(len(cases))]

    def holds(case: dict, judged: str) -> bool:
        return judged != case["skill"] if case["negative"] else judged == case["skill"]

    failures = 0
    undecided = 0
    unmeasured = 0
    per_skill: dict[str, list[int]] = {}
    for case, judged_runs in zip(cases, verdicts):
        # A judge call that errored (CLI failure, timeout, rate limit) measured
        # nothing. Counting it as a wrong answer turns a throttled run into
        # "rate=0.00, confirmed failure" — a whole batch once reported nine such
        # phantom failures. Drop errors from the denominator and report them.
        graded = [judged for judged in judged_runs if not judged.startswith("error:")]
        errored = len(judged_runs) - len(graded)
        if not graded:
            unmeasured += 1
            print(
                f"SKIP {case['skill']}#{case['id']} expected="
                f"{'NOT ' + case['skill'] if case['negative'] else case['skill']} "
                f"judged=all {errored} run(s) errored: {judged_runs[0][:70]}"
            )
            continue
        holding = sum(holds(case, judged) for judged in graded)
        rate = holding / len(graded)
        passed = rate >= args.trigger_threshold
        if runs == 1:
            judged = judged_runs[0]
        else:
            low, high = wilson_interval(holding, len(graded))
            # The verdict only means something if the whole interval sits on one
            # side of the threshold; otherwise this N cannot tell them apart.
            straddles = low <= args.trigger_threshold <= high
            undecided += straddles
            dropped = f" ({errored} errored)" if errored else ""
            judged = (
                f"rate={rate:.2f} CI[{low:.2f},{high:.2f}]{'?' if straddles else ''}{dropped} "
                f"{','.join(sorted(set(graded)))}"
            )
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
    if unmeasured:
        print(f"note: {unmeasured} case(s) SKIPped — every judge call errored, so nothing was measured for them")
    if undecided:
        print(f"note: {undecided} case(s) marked ? — the confidence interval straddles the threshold, so this N decides nothing about them")
    for name, (passed_count, total) in sorted(per_skill.items()):
        print(f"{name}: {passed_count}/{total}")
    measured = len(cases) - unmeasured
    tail = f", {unmeasured} unmeasured" if unmeasured else ""
    print(f"total: {measured - failures}/{measured} passed (model={args.model}, runs={runs}{tail})")
    # An unmeasured case is not a pass: exiting 0 here would report success for
    # work that never ran.
    return 1 if failures or unmeasured else 0


if __name__ == "__main__":
    sys.exit(main())
