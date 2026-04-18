from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def load_evals(relative_path: str) -> list[dict]:
    data = json.loads((ROOT / relative_path).read_text())
    return data["evals"]


class ReuseBoundaryRuleTests(unittest.TestCase):
    def test_legacy_skill_states_reuse_default_and_exception_boundary(self):
        text = load_text("legacy-component-skinning/SKILL.md")

        self.assertIn("默认优先复用共享层", text)
        self.assertIn("页面特有结构差异", text)
        self.assertIn("错误耦合", text)
        self.assertIn("必须记录原因", text)

    def test_xylink_skill_states_reuse_default_and_exception_boundary(self):
        text = load_text("xylink-legacy-component-skinning/SKILL.md")

        self.assertIn("默认优先复用共享层", text)
        self.assertIn("页面特有结构差异", text)
        self.assertIn("错误耦合", text)
        self.assertIn("必须记录原因", text)

    def test_legacy_evals_cover_do_not_over_abstract_single_page_fix(self):
        evals = load_evals("legacy-component-skinning/evals/evals.json")
        by_id = {item["id"]: item for item in evals}

        self.assertIn(14, by_id)
        self.assertIn("只在一个页面", by_id[14]["prompt"])
        self.assertIn("不要为了复用而过度抽象", by_id[14]["expected_output"])

    def test_xylink_evals_cover_do_not_over_abstract_single_page_fix(self):
        evals = load_evals("xylink-legacy-component-skinning/evals/evals.json")
        by_id = {item["id"]: item for item in evals}

        self.assertIn(14, by_id)
        self.assertIn("只在一个页面", by_id[14]["prompt"])
        self.assertIn("不要为了复用而过度抽象", by_id[14]["expected_output"])


if __name__ == "__main__":
    unittest.main()
