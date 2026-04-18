from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def extract_description(relative_path: str) -> str:
    text = (ROOT / relative_path).read_text()
    match = re.search(r'^description:\s*"?(.+?)"?\s*$', text, re.MULTILINE)
    if not match:
        raise AssertionError(f"description not found in {relative_path}")
    return match.group(1)


class FrontmatterDescriptionTests(unittest.TestCase):
    def test_legacy_skill_description_starts_with_use_when(self):
        description = extract_description("legacy-component-skinning/SKILL.md")
        self.assertTrue(description.startswith("Use when"))

    def test_xylink_skill_description_starts_with_use_when(self):
        description = extract_description("xylink-legacy-component-skinning/SKILL.md")
        self.assertTrue(description.startswith("Use when"))


if __name__ == "__main__":
    unittest.main()
