from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_evals(relative_path: str) -> list[dict]:
    data = json.loads((ROOT / relative_path).read_text())
    return data["evals"]


class SkillEvalCoverageTests(unittest.TestCase):
    def test_legacy_skinning_has_realistic_dry_run_cases(self):
        evals = load_evals("legacy-component-skinning/evals/evals.json")
        by_id = {item["id"]: item for item in evals}

        self.assertGreaterEqual(len(evals), 13)
        self.assertIn(12, by_id)
        self.assertIn(13, by_id)
        self.assertIn("manifest", by_id[12]["expected_output"])
        self.assertIn("unverified", by_id[12]["expected_output"])
        self.assertIn("happy path", by_id[13]["prompt"])
        self.assertIn("unverified", by_id[13]["expected_output"])

    def test_xylink_skinning_has_realistic_dry_run_cases(self):
        evals = load_evals("xylink-legacy-component-skinning/evals/evals.json")
        by_id = {item["id"]: item for item in evals}

        self.assertGreaterEqual(len(evals), 13)
        self.assertIn(12, by_id)
        self.assertIn(13, by_id)
        self.assertIn("manifest", by_id[12]["expected_output"])
        self.assertIn("unverified", by_id[12]["expected_output"])
        self.assertIn("happy path", by_id[13]["prompt"])
        self.assertIn("unverified", by_id[13]["expected_output"])


if __name__ == "__main__":
    unittest.main()
