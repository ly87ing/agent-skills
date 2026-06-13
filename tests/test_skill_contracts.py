from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULE_DERIVED_SKILLS = {
    "architecture-change-review",
    "artifact-hygiene",
    "code-style-contracts",
    "frontend-verification",
    "reader-facing-writing",
}
RETIRED_SKILLS = {
    "legacy-component-skinning",
    "legacy-component-skinning",
}


def skill_dirs() -> list[Path]:
    return sorted(
        path
        for path in ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    )


def read_frontmatter(skill_dir: Path) -> dict[str, str]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise AssertionError(f"frontmatter missing: {skill_dir.name}")
    frontmatter = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter


class SkillContractTests(unittest.TestCase):
    def test_all_skills_have_open_standard_frontmatter(self):
        for skill_dir in skill_dirs():
            frontmatter = read_frontmatter(skill_dir)
            name = frontmatter.get("name")
            description = frontmatter.get("description", "")

            self.assertEqual(name, skill_dir.name)
            self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertLessEqual(len(name), 64)
            self.assertGreaterEqual(len(description), 40, name)
            self.assertLessEqual(len(description), 1024, name)
            self.assertNotIn("TODO", (skill_dir / "SKILL.md").read_text(encoding="utf-8"), name)

    def test_rule_derived_skills_exist_and_retired_skinning_skills_are_absent(self):
        current = {path.name for path in skill_dirs()}

        self.assertTrue(RULE_DERIVED_SKILLS.issubset(current))
        self.assertTrue(current.isdisjoint(RETIRED_SKILLS))
        for skill_name in RETIRED_SKILLS:
            self.assertFalse((ROOT / skill_name).exists(), skill_name)

    def test_rule_derived_skills_preserve_agent_manager_rule_intent(self):
        expected_phrases = {
            "architecture-change-review": [
                "dependency direction",
                "config",
                "rollback path",
            ],
            "artifact-hygiene": [
                "Disposable run artifacts",
                "Playwright",
                "gitignore",
            ],
            "code-style-contracts": [
                "Validate inputs fail-close",
                "formatter",
                "comments",
            ],
            "frontend-verification": [
                "Choose the browser tool by intent",
                "Playwright",
                "Chrome DevTools",
            ],
            "reader-facing-writing": [
                "reader",
                "source truth",
                "HTML",
            ],
        }
        for skill_name, phrases in expected_phrases.items():
            text = (ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text, skill_name)

    def test_openai_metadata_default_prompts_reference_skill_names(self):
        for skill_dir in skill_dirs():
            metadata_path = skill_dir / "agents" / "openai.yaml"
            if not metadata_path.exists():
                continue
            metadata = metadata_path.read_text(encoding="utf-8")
            self.assertIn(f"${skill_dir.name}", metadata)


if __name__ == "__main__":
    unittest.main()
