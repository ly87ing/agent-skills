from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PressureScenarioResourceTests(unittest.TestCase):
    def test_legacy_skill_exposes_pressure_scenarios(self):
        skill = (ROOT / "legacy-component-skinning/SKILL.md").read_text()
        reference = ROOT / "legacy-component-skinning/references/pressure-scenarios.md"

        self.assertTrue(reference.exists())
        content = reference.read_text()
        self.assertIn("pressure-scenarios.md", skill)
        self.assertIn("Baseline", content)
        self.assertIn("With Skill", content)
        self.assertIn("manifest", content)
        self.assertIn("unverified", content)

    def test_xylink_skill_exposes_pressure_scenarios(self):
        skill = (ROOT / "xylink-legacy-component-skinning/SKILL.md").read_text()
        reference = ROOT / "xylink-legacy-component-skinning/references/pressure-scenarios.md"

        self.assertTrue(reference.exists())
        content = reference.read_text()
        self.assertIn("pressure-scenarios.md", skill)
        self.assertIn("Baseline", content)
        self.assertIn("With Skill", content)
        self.assertIn("manifest", content)
        self.assertIn("unverified", content)


if __name__ == "__main__":
    unittest.main()
