"""Regression guard for the mixed weight+units distribution.

Fixed `units` allocations are reserved first and the remainder is split by
`weight`. The weighted accumulator must be seeded with the fixed total so the
loop guards (which compare against the full target_units) stay correct.
Regressing this silently over-fills the day (sum > target, exit 0) or rejects
valid plans with a spurious PlanError.
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


if __name__ == "__main__":
    unittest.main()
