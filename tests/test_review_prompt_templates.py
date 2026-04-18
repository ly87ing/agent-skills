from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReviewPromptTemplateTests(unittest.TestCase):
    def test_legacy_skill_has_review_prompt_templates_reference(self):
        skill = (ROOT / "legacy-component-skinning/SKILL.md").read_text()
        reference = ROOT / "legacy-component-skinning/references/review-prompt-templates.md"

        self.assertTrue(reference.exists())
        content = reference.read_text()
        self.assertIn("review-prompt-templates.md", skill)
        self.assertIn("实施补漏 review prompt", content)
        self.assertIn("验收 review prompt", content)
        self.assertIn("manifest", content)
        self.assertIn("unverified", content)

    def test_xylink_skill_has_review_prompt_templates_reference(self):
        skill = (ROOT / "xylink-legacy-component-skinning/SKILL.md").read_text()
        reference = ROOT / "xylink-legacy-component-skinning/references/review-prompt-templates.md"

        self.assertTrue(reference.exists())
        content = reference.read_text()
        self.assertIn("review-prompt-templates.md", skill)
        self.assertIn("实施补漏 review prompt", content)
        self.assertIn("验收 review prompt", content)
        self.assertIn("manifest", content)
        self.assertIn("unverified", content)


if __name__ == "__main__":
    unittest.main()
