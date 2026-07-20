#!/usr/bin/env python3
# Requires Python 3.10+ (uses zip(strict=True)). Standard library only, no third-party deps.
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


# ONES stores manhours as integer "units"; 800000 units == one 8-hour workday.
# This is a fixed definition used to express day fractions, independent of the
# per-run fill target below.
UNITS_PER_WORKDAY = 800000
# Default fill target is one full workday unless the caller overrides target_units.
DEFAULT_TARGET_UNITS = UNITS_PER_WORKDAY
# Default rounding step for weighted allocations: 80000 units == 0.1 workday.
# Explicit fixed units are preserved independently of this step.
DEFAULT_UNIT_STEP = 80000
# ONES manhour timestamps are local; default to UTC+8 unless the plan sets timezone_offset_hours.
DEFAULT_TIMEZONE_OFFSET_HOURS = 8
# Per-allocation manhour descriptions are capped at this length and rejected
# pre-write if longer, keeping entries concise and within a safe bound for the
# ONES manhour description field.
MAX_DESCRIPTION_CHARS = 240


class PlanError(ValueError):
    pass


def load_plan(path: Path) -> dict[str, Any]:
    try:
        raw_text = sys.stdin.read() if str(path) == "-" else path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except FileNotFoundError as exc:
        raise PlanError(f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PlanError(f"input file is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PlanError("input JSON must be an object")
    return data


def require_int(value: Any, field: str, *, minimum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise PlanError(f"{field} must be an integer")
    if minimum is not None and value < minimum:
        raise PlanError(f"{field} must be >= {minimum}")
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{field} must be a non-empty string")
    return value.strip()


def parse_date(raw_date: Any, timezone_offset_hours: int) -> int:
    date_text = require_string(raw_date, "date")
    try:
        parsed = datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError as exc:
        raise PlanError("date must use YYYY-MM-DD") from exc
    tz = timezone(timedelta(hours=timezone_offset_hours))
    return int(parsed.replace(tzinfo=tz).timestamp())


def round_down_to_step(value: int, step: int) -> int:
    return value - (value % step)


def distribute_units(allocations: list[dict[str, Any]], target_units: int, unit_step: int) -> list[int]:
    fixed_units: list[int | None] = []
    weighted_indexes: list[int] = []
    total_fixed = 0

    for index, item in enumerate(allocations):
        if "units" in item and item["units"] is not None:
            units = require_int(item["units"], f"allocations[{index}].units", minimum=1)
            fixed_units.append(units)
            total_fixed += units
        else:
            weight = item.get("weight", 1)
            if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight <= 0:
                raise PlanError(f"allocations[{index}].weight must be a positive number")
            fixed_units.append(None)
            weighted_indexes.append(index)

    if total_fixed > target_units:
        raise PlanError("fixed units exceed target_units")
    if total_fixed == target_units and weighted_indexes:
        raise PlanError("weighted allocations remain after fixed units already fill target_units")

    result = [units if units is not None else 0 for units in fixed_units]
    remaining = target_units - total_fixed
    if not weighted_indexes:
        if remaining != 0:
            raise PlanError("fixed units do not sum to target_units")
        return result

    if remaining < unit_step:
        raise PlanError("remaining units are too small for weighted allocation")
    if remaining % unit_step != 0:
        raise PlanError("remaining weighted units must be a multiple of unit_step")

    total_weight = sum(float(allocations[index].get("weight", 1)) for index in weighted_indexes)
    assigned = total_fixed
    remainders: list[tuple[float, int]] = []
    for index in weighted_indexes:
        exact = remaining * float(allocations[index].get("weight", 1)) / total_weight
        rounded = round_down_to_step(int(exact), unit_step)
        if rounded == 0:
            rounded = unit_step
        result[index] = rounded
        assigned += rounded
        remainders.append((exact - rounded, index))

    while assigned > target_units:
        candidates = [index for index in weighted_indexes if result[index] > unit_step]
        if not candidates:
            raise PlanError("cannot reduce weighted allocations without dropping below unit_step")
        index = min(candidates, key=lambda item_index: result[item_index])
        result[index] -= unit_step
        assigned -= unit_step

    for _, index in sorted(remainders, reverse=True):
        if assigned >= target_units:
            break
        result[index] += unit_step
        assigned += unit_step

    if assigned != target_units:
        raise PlanError("unable to distribute units to match target_units")
    return result


def normalize(plan: dict[str, Any]) -> dict[str, Any]:
    target_units = require_int(plan.get("target_units", DEFAULT_TARGET_UNITS), "target_units", minimum=1)
    unit_step = require_int(plan.get("unit_step", DEFAULT_UNIT_STEP), "unit_step", minimum=1)
    timezone_offset_hours = require_int(
        plan.get("timezone_offset_hours", DEFAULT_TIMEZONE_OFFSET_HOURS),
        "timezone_offset_hours",
    )
    raw_allocations = plan.get("allocations")
    if not isinstance(raw_allocations, list) or not raw_allocations:
        raise PlanError("allocations must be a non-empty list")
    allocations: list[dict[str, Any]] = []
    seen_tasks: set[str] = set()

    for index, raw_item in enumerate(raw_allocations):
        if not isinstance(raw_item, dict):
            raise PlanError(f"allocations[{index}] must be an object")
        task_uuid = require_string(raw_item.get("task_uuid"), f"allocations[{index}].task_uuid")
        if task_uuid in seen_tasks:
            raise PlanError(f"duplicate task_uuid: {task_uuid}")
        seen_tasks.add(task_uuid)
        task_number = require_int(raw_item.get("task_number"), f"allocations[{index}].task_number", minimum=1)
        task_name = require_string(raw_item.get("task_name"), f"allocations[{index}].task_name")
        description = require_string(raw_item.get("description"), f"allocations[{index}].description")
        if len(description) > MAX_DESCRIPTION_CHARS:
            raise PlanError(f"allocations[{index}].description is too long")
        item = {
            "task_uuid": task_uuid,
            "task_number": task_number,
            "task_name": task_name,
            "description": description,
        }
        if "units" in raw_item:
            item["units"] = raw_item["units"]
        if "weight" in raw_item:
            item["weight"] = raw_item["weight"]
        allocations.append(item)

    units = distribute_units(allocations, target_units, unit_step)
    start_time = parse_date(plan.get("date"), timezone_offset_hours)
    normalized_allocations = []
    for item, unit_count in zip(allocations, units, strict=True):
        normalized_allocations.append(
            {
                "task_uuid": item["task_uuid"],
                "task_number": item["task_number"],
                "task_name": item["task_name"],
                "hours": unit_count,
                "day_fraction": round(unit_count / UNITS_PER_WORKDAY, 4),
                "description": item["description"],
            }
        )

    return {
        "date": require_string(plan.get("date"), "date"),
        "start_time": start_time,
        "target_units": target_units,
        "unit_step": unit_step,
        "timezone_offset_hours": timezone_offset_hours,
        "total_units": sum(item["hours"] for item in normalized_allocations),
        "total_days": round(sum(item["hours"] for item in normalized_allocations) / UNITS_PER_WORKDAY, 4),
        "allocations": normalized_allocations,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize and validate an ONES manhour allocation plan")
    parser.add_argument("input", type=Path, help="Path to a JSON allocation plan, or - for stdin")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = normalize(load_plan(args.input))
    except PlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
