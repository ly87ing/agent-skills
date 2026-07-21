"""Regression guards for mixed distribution and exact fixed-hour plans.

Fixed `units` allocations are reserved first and the remainder is split by
`weight`. The weighted accumulator must be seeded with the fixed total so the
loop guards (which compare against the full target_units) stay correct.
Regressing this silently over-fills the day (sum > target, exit 0) or rejects
valid plans with a spurious PlanError. Fixed clock-hour plans must also remain
valid when their units do not align to the weighted-allocation rounding step.
"""

import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "normalize_manhour_plan.py"


def _load():
    spec = importlib.util.spec_from_file_location("normalize_manhour_plan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DistributeUnitsMixedTests(unittest.TestCase):
    def setUp(self):
        self.m = _load()
        self.step = self.m.DEFAULT_UNIT_STEP

    def test_mixed_fixed_and_weight_sums_to_target(self):
        result = self.m.distribute_units([{"weight": 3}, {"units": 80000}], 480000, self.step)
        self.assertEqual(sum(result), 480000)
        self.assertEqual(result[1], 80000)  # fixed allocation preserved verbatim

    def test_mixed_valid_plan_not_rejected(self):
        result = self.m.distribute_units(
            [{"weight": 1}, {"weight": 1}, {"units": 240000}], 480000, self.step
        )
        self.assertEqual(sum(result), 480000)

    def test_pure_weight_and_pure_fixed_still_work(self):
        self.assertEqual(
            sum(self.m.distribute_units([{"weight": 1}, {"weight": 1}], 480000, self.step)), 480000
        )
        self.assertEqual(
            sum(self.m.distribute_units([{"units": 240000}, {"units": 240000}], 480000, self.step)), 480000
        )

    def test_explicit_clock_hours_are_preserved_outside_weight_step(self):
        result = self.m.distribute_units(
            [
                {"units": 400000},
                {"units": 100000},
                {"units": 200000},
                {"units": 100000},
            ],
            800000,
            self.step,
        )
        self.assertEqual(result, [400000, 100000, 200000, 100000])

    def test_incompatible_weighted_remainder_requires_a_smaller_step(self):
        with self.assertRaisesRegex(
            self.m.PlanError, "remaining weighted units must be a multiple of unit_step"
        ):
            self.m.distribute_units([{"units": 100000}, {"weight": 1}], 800000, self.step)

    def test_normalize_accepts_a_one_hour_fixed_target(self):
        result = self.m.normalize(
            {
                "date": "2026-07-20",
                "target_units": 100000,
                "unit_step": self.step,
                "allocations": [
                    {
                        "task_uuid": "TASK_UUID",
                        "task_number": 100200,
                        "task_name": "Project support",
                        "units": 100000,
                        "description": "Environment support",
                    }
                ],
            }
        )
        self.assertEqual(result["total_units"], 100000)
        self.assertEqual(result["allocations"][0]["hours"], 100000)
        # start_time must be midnight UTC+8, not midnight in the machine's zone.
        self.assertEqual(result["start_time"], 1784476800)

    def test_parse_date_anchors_midnight_to_the_requested_offset(self):
        self.assertEqual(self.m.parse_date("2026-07-20", 8), 1784476800)
        self.assertEqual(self.m.parse_date("2026-07-20", 0), 1784505600)

    def test_parse_date_rejects_an_out_of_range_offset(self):
        with self.assertRaisesRegex(self.m.PlanError, "timezone_offset_hours must be <= 23"):
            self.m.normalize(
                {
                    "date": "2026-07-20",
                    "target_units": 100000,
                    "unit_step": self.step,
                    "timezone_offset_hours": 99,
                    "allocations": [
                        {
                            "task_uuid": "TASK_UUID",
                            "task_number": 100200,
                            "task_name": "Project support",
                            "units": 100000,
                            "description": "Environment support",
                        }
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
