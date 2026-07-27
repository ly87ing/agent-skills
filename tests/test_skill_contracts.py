from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAINTAINED_SKILLS = {
    "artifact-hygiene",
    "change-discipline",
    "frontend-verification",
    "reader-facing-writing",
    "safe-merge-review",
}
RULE_DERIVED_SKILLS = {
    "artifact-hygiene",
    "change-discipline",
    "frontend-verification",
    "reader-facing-writing",
}
RETIRED_SKILLS = {
    "legacy-component-skinning",
    "legacy-component-skinning",
}
RUNTIME_ADAPTERS = {
    "antigravity.md",
    "claude.md",
    "codex.md",
}
FORBIDDEN_CORE_RUNTIME_TERMS = {
    "AskUserQuestion",
    "TaskCreate",
    "TodoWrite",
    "Read 工具",
    "update_plan",
}
# CJK punctuation + kana + ideographs + fullwidth forms. Distribution-layer
# content (SKILL.md, references/, agents/, openai.*) must stay all-English;
# embed any CJK literal a script needs as a \u escape. Sole carve-out: an
# eval's "prompt" simulates real user phrasing, and the primary user phrases
# requests in Chinese \u2014 see test_skill_content_is_english_only.
CJK_PATTERN = re.compile(r"[\u3000-\u303f\u3040-\u30ff\u4e00-\u9fff\uff00-\uffef]")


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
    def test_current_skill_inventory_matches_maintained_set(self):
        current = {path.name for path in skill_dirs()}

        self.assertEqual(current, MAINTAINED_SKILLS)

    def test_all_skills_have_open_standard_frontmatter(self):
        for skill_dir in skill_dirs():
            frontmatter = read_frontmatter(skill_dir)
            name = frontmatter.get("name")
            description = frontmatter.get("description", "")

            self.assertEqual(name, skill_dir.name)
            self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertLessEqual(len(name), 64)
            # Open-standard naming rule: names may not contain the reserved
            # words "anthropic" or "claude".
            for reserved_word in ("anthropic", "claude"):
                self.assertNotIn(reserved_word, name, name)
            self.assertGreaterEqual(len(description), 40, name)
            self.assertLessEqual(len(description), 1024, name)
            self.assertNotIn("TODO", (skill_dir / "SKILL.md").read_text(encoding="utf-8"), name)

    def test_skill_frontmatter_parses_as_yaml(self):
        # The naive line-split reader above tolerates frontmatter that real
        # YAML parsers (Codex, Claude Code, skills-ref) reject — e.g. an
        # unquoted scalar containing ": " (colon-space). Validate with a real
        # parser so a broken description can't ship and silently fail to load.
        try:
            import yaml
        except ImportError:
            yaml = None

        for skill_dir in skill_dirs():
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
            self.assertIsNotNone(match, f"{skill_dir.name}: missing frontmatter")
            block = match.group(1)

            if yaml is not None:
                try:
                    data = yaml.safe_load(block)
                except yaml.YAMLError as exc:
                    raise AssertionError(f"{skill_dir.name}: SKILL.md frontmatter is not valid YAML: {exc}")
                self.assertIsInstance(data, dict, skill_dir.name)
                self.assertEqual(data.get("name"), skill_dir.name, skill_dir.name)
                self.assertTrue(str(data.get("description", "")).strip(), skill_dir.name)
            else:
                # Dependency-free fallback: an unquoted plain scalar value must
                # not contain ": " or " #", which break YAML parsing.
                for line in block.splitlines():
                    if ":" not in line:
                        continue
                    key, value = line.split(":", 1)
                    value = value.strip()
                    if value and value[0] not in "\"'":
                        self.assertNotIn(": ", value, f"{skill_dir.name}: unquoted '{key.strip()}' breaks YAML")
                        self.assertNotIn(" #", value, f"{skill_dir.name}: unquoted '{key.strip()}' breaks YAML")

    def test_skill_bodies_are_runtime_neutral(self):
        for skill_dir in skill_dirs():
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            for runtime_term in FORBIDDEN_CORE_RUNTIME_TERMS:
                self.assertNotIn(runtime_term, skill_text, skill_dir.name)

    def test_skill_bodies_stay_progressively_disclosed(self):
        for skill_dir in skill_dirs():
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertLessEqual(len(skill_text.splitlines()), 500, skill_dir.name)

            for forbidden_doc_name in ("README.md", "CHANGELOG.md", "INSTALL.md", "INSTALLATION.md"):
                self.assertFalse((skill_dir / forbidden_doc_name).exists(), f"{skill_dir.name}/{forbidden_doc_name}")

            references_dir = skill_dir / "references"
            if references_dir.exists():
                for reference_path in references_dir.glob("**/*"):
                    if reference_path.is_file():
                        self.assertEqual(reference_path.parent, references_dir, str(reference_path))

            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                for script_path in scripts_dir.glob("**/*"):
                    if "__pycache__" in script_path.parts or script_path.suffix == ".pyc":
                        continue
                    if script_path.is_file():
                        self.assertEqual(script_path.parent, scripts_dir, str(script_path))

            agents_dir = skill_dir / "agents"
            self.assertTrue(agents_dir.exists(), skill_dir.name)
            allowed_agent_files = {"openai.yaml"} | RUNTIME_ADAPTERS
            current_agent_files = {path.name for path in agents_dir.iterdir() if path.is_file()}
            self.assertEqual(current_agent_files, allowed_agent_files, skill_dir.name)

    def test_rule_derived_skills_exist_and_retired_skinning_skills_are_absent(self):
        current = {path.name for path in skill_dirs()}

        self.assertTrue(RULE_DERIVED_SKILLS.issubset(current))
        self.assertTrue(current.isdisjoint(RETIRED_SKILLS))
        for skill_name in RETIRED_SKILLS:
            self.assertFalse((ROOT / skill_name).exists(), skill_name)

    def test_rule_derived_skills_preserve_agent_manager_rule_intent(self):
        expected_phrases = {
            "change-discipline": [
                "dependency direction",
                "config",
                "rollback path",
                "Validate inputs fail-close",
                "formatter",
                "comments",
            ],
            "artifact-hygiene": [
                "Disposable run artifacts",
                "Playwright",
                "gitignore",
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

    def test_openai_metadata_is_present_and_references_skill_names(self):
        for skill_dir in skill_dirs():
            metadata_path = skill_dir / "agents" / "openai.yaml"
            self.assertTrue(metadata_path.exists(), skill_dir.name)

            metadata = metadata_path.read_text(encoding="utf-8")
            self.assertIn("interface:", metadata, skill_dir.name)
            self.assertRegex(metadata, r'(?m)^\s+display_name: ".+"$', skill_dir.name)
            short_description = re.search(r'(?m)^\s+short_description: "(.+)"$', metadata)
            self.assertIsNotNone(short_description, skill_dir.name)
            self.assertGreaterEqual(len(short_description.group(1)), 25, skill_dir.name)
            self.assertLessEqual(len(short_description.group(1)), 64, skill_dir.name)
            self.assertRegex(metadata, r'(?m)^\s+default_prompt: ".+"$', skill_dir.name)
            self.assertIn(f"${skill_dir.name}", metadata)

    def test_every_skill_has_well_formed_trigger_evals(self):
        for skill_dir in skill_dirs():
            evals_path = skill_dir / "evals" / "evals.json"
            self.assertTrue(evals_path.exists(), f"{skill_dir.name}/evals/evals.json missing")
            try:
                payload = json.loads(evals_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{skill_dir.name}: evals.json is not valid JSON: {exc}")

            self.assertIsInstance(payload, dict, skill_dir.name)
            self.assertEqual(payload.get("skill_name"), skill_dir.name, skill_dir.name)

            cases = payload.get("evals")
            self.assertIsInstance(cases, list, skill_dir.name)
            self.assertGreaterEqual(len(cases), 3, skill_dir.name)
            seen_ids: set = set()
            for index, case in enumerate(cases):
                self.assertTrue(str(case.get("prompt", "")).strip(), f"{skill_dir.name}#{index} empty prompt")
                expectation = str(case.get("expected_output", "")).strip()
                self.assertTrue(expectation, f"{skill_dir.name}#{index} empty expected_output")

                # The runners select cases by id and classify them by this prefix.
                # A duplicate id makes --ids ambiguous; a graded expectation
                # ("should not STRONGLY trigger") reads as an absolute negative and
                # fails a correct answer — as change-discipline#5 did until it was
                # rewritten. A binary harness needs binary expectations.
                case_id = case.get("id")
                self.assertIsInstance(case_id, int, f"{skill_dir.name}#{index} id must be an int")
                self.assertNotIn(case_id, seen_ids, f"{skill_dir.name}: duplicate eval id {case_id}")
                seen_ids.add(case_id)
                self.assertRegex(
                    expectation,
                    r"(?i)^should\s+(not\s+)?trigger\b",
                    f"{skill_dir.name}#{case_id}: expected_output must open with "
                    "'Should trigger' or 'Should NOT trigger' and state one side, not a degree",
                )

    def test_long_reference_files_start_with_a_table_of_contents(self):
        for skill_dir in skill_dirs():
            references_dir = skill_dir / "references"
            if not references_dir.exists():
                continue
            for reference_path in sorted(references_dir.glob("*.md")):
                lines = reference_path.read_text(encoding="utf-8").splitlines()
                if len(lines) <= 100:
                    continue
                head = "\n".join(lines[:12])
                self.assertIn(
                    "Table of Contents",
                    head,
                    f"{skill_dir.name}/references/{reference_path.name} (>100 lines) needs a top-of-file Table of Contents",
                )

    def test_skill_descriptions_stay_third_person(self):
        # The skill must describe itself in third person, but quoted trigger
        # examples may quote a user's own words ("fix my bugs"), so strip
        # quoted spans before checking the skill's own voice.
        first_second_person = re.compile(r"\b(I|I'm|I'll|my|we|We|us|our|Our|you|You|your|Your|yours)\b")
        for skill_dir in skill_dirs():
            description = read_frontmatter(skill_dir).get("description", "")
            unquoted = re.sub(r"\"[^\"]*\"|'[^']*'", "", description)
            match = first_second_person.search(unquoted)
            self.assertIsNone(
                match,
                f"{skill_dir.name}: description must be third person, found '{match.group(0) if match else ''}'",
            )

    def test_skill_content_is_english_only(self):
        text_suffixes = {".md", ".json", ".yaml", ".yml"}
        targets = []
        for skill_dir in skill_dirs():
            targets.extend(
                path
                for path in sorted(skill_dir.rglob("*"))
                if path.is_file() and path.suffix in text_suffixes and "__pycache__" not in path.parts
            )
        readme = ROOT / "README.md"
        if readme.exists():
            targets.append(readme)

        for path in targets:
            text = path.read_text(encoding="utf-8")
            if path.name == "evals.json" and path.parent.name == "evals":
                # Eval prompts simulate real user phrasing and may be written
                # in the primary user's language (Chinese); a blanket CJK ban
                # here left Chinese triggering permanently untested. Every
                # other evals.json field stays English.
                payload = json.loads(text)
                fields = [str(payload.get("skill_name", ""))]
                for case in payload.get("evals", []):
                    fields.extend(str(value) for key, value in case.items() if key != "prompt")
                for field in fields:
                    self.assertIsNone(
                        CJK_PATTERN.search(field),
                        f"{path.relative_to(ROOT)}: non-prompt eval field contains "
                        f"non-English content: {field!r}",
                    )
                continue
            match = CJK_PATTERN.search(text)
            if match:
                line_no = text[: match.start()].count("\n") + 1
                raise AssertionError(
                    f"{path.relative_to(ROOT)}:{line_no} contains non-English character "
                    f"{match.group(0)!r}; skill content and README must be all English"
                )

    def test_runtime_adapters_are_thin_and_core_referenced(self):
        for skill_dir in skill_dirs():
            for adapter_name in RUNTIME_ADAPTERS:
                adapter_path = skill_dir / "agents" / adapter_name
                self.assertTrue(adapter_path.exists(), f"{skill_dir.name}/{adapter_name}")
                adapter = adapter_path.read_text(encoding="utf-8")

                self.assertIn("Core source of truth: `SKILL.md`.", adapter, f"{skill_dir.name}/{adapter_name}")
                self.assertIn("Do not duplicate or weaken", adapter, f"{skill_dir.name}/{adapter_name}")
                self.assertLessEqual(len(adapter.splitlines()), 20, f"{skill_dir.name}/{adapter_name}")

            claude_adapter = (skill_dir / "agents" / "claude.md").read_text(encoding="utf-8")
            codex_adapter = (skill_dir / "agents" / "codex.md").read_text(encoding="utf-8")
            antigravity_adapter = (skill_dir / "agents" / "antigravity.md").read_text(encoding="utf-8")
            self.assertIn(f"/{skill_dir.name}", claude_adapter, skill_dir.name)
            self.assertIn(f"${skill_dir.name}", codex_adapter, skill_dir.name)
            self.assertIn("Antigravity CLI", antigravity_adapter, skill_dir.name)
            self.assertIn(skill_dir.name, antigravity_adapter, skill_dir.name)


if __name__ == "__main__":
    unittest.main()
