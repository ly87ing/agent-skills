---
name: ones-manhour-fill
description: Fills ONES manhour records from a daily work summary into a specific parent task's subtasks, with reasonable one-day allocation, existing-record checks, safe add-only writes, and post-write verification. Use when a user asks to register, backfill, complete, or distribute daily ONES work hours/worklogs/manhours from chat notes or a work summary into a parent task, especially when the request includes a date plus an ONES parent task URL, number, or uuid. For ONES bug fixing or QA evidence routing use internal-bug-loop; for pure ONES queries use the ONES connector directly.
---

# ONES Manhour Fill

Daily ONES manhour backfill for "one date x one parent task x the current ONES identity".
The skill turns a work summary into a small set of subtask allocations, writes only the missing records, and verifies the final total.

## Scope

Use this skill only for ONES manhour/worklog entries. The normal target is exactly one workday unless the user gives a different total.

| Scenario | Use |
|---|---|
| Fill one date of work from a chat summary into a parent task's subtasks | this skill |
| Complete a partial day already recorded in ONES | this skill, add only the missing gap |
| Change or delete existing manhour records | stop unless explicitly requested |
| Query existing worklogs only | ONES connector |
| Fix, verify, or route defects | internal-bug-loop |

## Required Inputs

- Date, normalized to an absolute `YYYY-MM-DD`.
- Parent task link, number, or uuid.
- Daily work summary.
- Target total, default `800000` ONES units = 1 workday = 8 hours.
- Current ONES identity from the available ONES connector or project profile.

If the parent task is ambiguous, if the current ONES identity does not match the person being filled for, or if the date is missing, stop and ask for alignment before writing.

## Hard Constraints

1. Never echo ONES tokens, user ids, passwords, or cookie values.
2. Always read the parent task first and use only its actual subtasks; do not invent tasks or write to a nearby parent.
3. Always query existing manhours for the current owner and date before writing.
4. Prefer add-only behavior. Do not update or delete existing manhours unless the user explicitly requests correction.
5. Do not exceed the target total for the date. If existing unrelated records would make the target impossible, stop and report the conflict.
6. Use the date's local midnight as `start_time`, `type=recorded`, and detailed mode when the ONES API supports it.
7. Treat dry-run and successful writes as different states. Completion requires post-write readback showing the expected total.
8. Manhour descriptions must be neutral, factual, and professional. Never copy chat tone, jokes, sarcasm, venting, personal-life items, or names of people/conflicts into a description — these records are visible to managers and PMs.
9. Never fabricate work to reach the target. Only real work produces allocations; if the screened real work cannot plausibly fill the target, stop and ask instead of padding with invented or non-work entries.

## Workflow

### 1. Preflight

Resolve the ONES domain, team/space id, credential source, and current ONES user through the available ONES connector or project profile. Verify credentials exist without printing their values.

Confirm:

- current ONES user name/uuid
- target date
- target parent task number/name/uuid
- target total units

### 2. Discover Parent and Subtasks

Fetch the parent task detail using the stable task detail endpoint or equivalent connector action. Confirm:

- parent number/name matches the user's request
- `subtasks` is non-empty
- subtask number, uuid, name, and status are available

If no subtask fits a work category, use a catch-all subtask only when the parent actually has one. Otherwise stop and show the missing category.

### 3. Existing Manhour Guard

Query current owner's manhours for the target date. Prefer an owner-filtered query and local date filtering when an all-user date query is slow.

Classify existing records:

- same parent or selected subtasks
- other tasks on the same date
- total units already recorded

Decision:

- total already equals target: report no-op after showing the matching records
- total is below target: this is the normal fill-the-day case, so add `target - existing_total`; only skip the top-up if the user explicitly asked to log a partial amount
- total exceeds target or unrelated records make the plan unsafe: stop and ask

### 4. Build a Reasonable Allocation

Screen the summary before mapping — a daily summary is raw chat, not a clean worklog. Sort each item into one of three buckets:

- **Real work** — keep it and map it to a subtask below.
- **Non-work time** (leave, medical, offsite, team-building, meals, being away, late/early): never turn this into a work description. Trivial daily overhead (a lunch, a short break) is just part of a normal workday — ignore it. But if a material part of the day was genuinely not worked (e.g. half-day leave), flag it: the remaining real work may be too thin to fill the day. Leave/attendance normally belongs in the OA/attendance system, not in ONES project manhours.
- **Non-substantive noise** (jokes, sarcasm, venting, banter, emoji/reactions — "摸鱼"/"划水"/"啥也没干"): never write it verbatim. If real work hides under the tone (e.g. "被需求折磨改了一下午" → a requirement change), extract only the factual work and describe it neutrally; if nothing real remains, drop the item.

Then map the surviving real work to 3-6 subtask records. Keep the allocation readable rather than atomizing every chat item.

Use the actual subtask names as the taxonomy. Common mapping signals:

- design, architecture, feasibility, technical approach, review, or code quality discussion -> design/discussion or review subtask
- deployment, environment, resource, ECS, port mapping, package, test support, API process, mock support -> project support subtask
- security incident, vulnerability, attack, hotfix, production issue, traffic switch, migration problem -> online issue / incident analysis subtask
- meeting, sync, demo, cancellation, scheduling -> meeting sync subtask
- learning, summary, tool usage guidance -> learning summary subtask
- unclear residue -> other subtask, only if it exists

Descriptions should be short, factual, and tied to the work summary. Avoid vague text such as "daily work" or "miscellaneous support" when a more specific grouped description is available.

Run `scripts/normalize_manhour_plan.py` when weights or units need deterministic normalization. The script validates total units, rounds to the configured unit step, checks duplicate tasks, and emits JSON suitable for review before writing.

### 5. Dry-Run Review

Before writing, present or inspect a concise plan:

- date and local start timestamp
- parent task number/name
- each subtask number/name
- units and day fraction
- description
- existing records and final expected total

If the plan is surprising, too concentrated in one subtask, or depends on a weak mapping, adjust the plan before writing.

### 6. Write Additive Records

For each allocation, call the ONES manhour add endpoint or connector action with:

- owner = current ONES user uuid
- task = subtask uuid
- start_time = target date local midnight in seconds
- hours = allocation units (ONES units, e.g. 800000 for a full day — not literal clock hours)
- type = `recorded`
- mode = `detailed` when required
- description = reviewed description

Handle `Hour.TooMany` or duplicate/day-full errors as a skip, then immediately re-query instead of retrying blindly.

### 7. Verify and Report

Read back current owner's manhours for the same date after writes. Completion requires:

- expected number of new keys or documented skips
- final total units equals target
- every new record points to a child of the requested parent

Report only the useful summary: date, parent, subtask numbers, units/day fractions, generated manhour keys, final total, and any skipped or conflicting records.

## Script

`scripts/normalize_manhour_plan.py` accepts a JSON plan:

```json
{
  "date": "2026-06-18",
  "target_units": 800000,
  "timezone_offset_hours": 8,
  "unit_step": 80000,
  "allocations": [
    {
      "task_uuid": "TASK_UUID",
      "task_number": 100200,
      "task_name": "Project support",
      "weight": 3,
      "description": "Deployment environment and resource coordination"
    }
  ]
}
```

Use `weight` for proportional planning or `units` for fixed values. Mixed `weight` and `units` records are allowed; fixed units are reserved first, and remaining units are distributed by weight.

Run it as `python3 scripts/normalize_manhour_plan.py plan.json --pretty` (or pass `-` to read the plan from stdin); it requires Python 3.10+ and uses only the standard library. It echoes the plan and adds `start_time`, `total_units`, `total_days`, and per-allocation `hours` (units) and `day_fraction` — the fields the step 5 Dry-Run Review inspects.
