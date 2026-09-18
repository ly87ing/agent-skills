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
    "technical-diagramming",
}
RULE_DERIVED_SKILLS = {
    "artifact-hygiene",
    "change-discipline",
    "frontend-verification",
    "reader-facing-writing",
}
RETIRED_SKILLS = {
    "legacy-component-skinning",
}
# `agents/` carries exactly one file, and it is the only one a runtime reads.
# `agents/openai.yaml` is Codex's real convention (its own bundled skills ship
# that file and nothing else). The per-runtime `claude.md` / `codex.md` /
# `antigravity.md` notes this catalog used to ship were read by nobody: no
# SKILL.md referenced them, no distribution code opened them, and no runtime
# loads an unreferenced file from a skill directory. They were removed in
# favour of SKILL.md staying the single source of truth — do not re-add a
# per-runtime note without first naming what actually loads it.
ALLOWED_AGENT_FILES = {"openai.yaml"}
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
            self.assertNotRegex(name, r"<[^>]*>", name)
            # Open-standard naming rule: names may not contain the reserved
            # words "anthropic" or "claude".
            for reserved_word in ("anthropic", "claude"):
                self.assertNotIn(reserved_word, name, name)
            self.assertGreaterEqual(len(description), 40, name)
            self.assertLessEqual(len(description), 1024, name)
            self.assertNotRegex(description, r"<[^>]*>", name)
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
            # A line count is the wrong anchor for what a loaded skill actually costs:
            # these bodies run one long rule per line, so reader-facing-writing sat at
            # 22 KB across 92 lines — under a fifth of the 500-line cap while being the
            # heaviest thing in the catalog. Characters are what the context window
            # pays for, so cap those too. The limit is set just above today's largest
            # body: its job is to stop a silent slide back, not to dictate a target.
            # Raising it needs the same justification a rule-budget bump needs — say
            # which content earned the increase, in a comment here.
            self.assertLessEqual(len(skill_text), 16000, f"{skill_dir.name}: SKILL.md too large")

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
            current_agent_files = {path.name for path in agents_dir.iterdir() if path.is_file()}
            self.assertEqual(current_agent_files, ALLOWED_AGENT_FILES, skill_dir.name)

    def test_descriptions_stay_within_the_resident_budget(self):
        # Every description in this catalog is loaded into EVERY session before the
        # user types anything — they are the resident cost of the catalog, the way a
        # shared rule core is the resident cost of the rule layer. A per-description
        # cap already exists above (1024, the platform limit), but nothing watched the
        # sum, and six descriptions each written up against that cap add up to more
        # than twice the entire shared rule core.
        #
        # The cap is set just above today's total. It is not a target to fill: a
        # description earns length by covering a triggering scenario that is actually
        # being missed, and the same edit should be judged on trigger evals, not on
        # having room left. Raising this number requires naming, here, which skill's
        # triggering it bought.
        total = 0
        for skill_dir in skill_dirs():
            total += len(read_frontmatter(skill_dir).get("description", ""))
        self.assertLessEqual(total, 5200, f"resident description budget exceeded: {total}B")

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
                (
                    "Do not create or widen `.gitignore`, config conventions, or repository "
                    "directories just to host disposable outputs."
                ),
            ],
            "frontend-verification": [
                "Choose the browser tool by intent",
                "Use Playwright for reproducible assertions, regression coverage",
                "Use Chrome DevTools for one-off visual inspection",
                "Preserve authenticated context deliberately",
                "report that tool failure before falling back",
            ],
            "reader-facing-writing": [
                "reader",
                "source truth",
                "HTML",
            ],
        }
        # The assertion is that the rule's intent survives somewhere in the skill
        # PACKAGE, not that it sits in SKILL.md's main path. Scoping it to SKILL.md
        # was correct while every skill was a single file; once a skill splits its
        # facets into references/ (progressive disclosure), the same intent is still
        # loaded on demand and the old scope would forbid the split rather than
        # protect the intent.
        for skill_name, phrases in expected_phrases.items():
            skill_dir = ROOT / skill_name
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            references_dir = skill_dir / "references"
            if references_dir.exists():
                for reference_path in sorted(references_dir.glob("*.md")):
                    text += "\n" + reference_path.read_text(encoding="utf-8")
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

    def test_behaviour_prompts_inline_what_their_case_only_names(self):
        # `behaviour_prompt` exists because one prompt cannot serve both harnesses.
        # run_trigger_evals.py needs the words a user really opens with, and real
        # openings routinely name material they do not carry ("this iteration's
        # to-do items"); run_behaviour_evals.py needs that material present, or
        # both arms fail identically and the case measures nothing. The field is
        # opt-in, so the failure mode to guard is not absence but a copy that
        # silently measures the same unmeasurable thing, or one parked on a
        # negative case the behaviour runner never reads.
        for skill_dir in skill_dirs():
            payload = json.loads((skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"))
            for case in payload.get("evals", []):
                if "behaviour_prompt" not in case:
                    continue
                case_id = case.get("id")
                behaviour = str(case["behaviour_prompt"]).strip()
                self.assertTrue(behaviour, f"{skill_dir.name}#{case_id}: empty behaviour_prompt")
                self.assertNotEqual(
                    behaviour,
                    str(case.get("prompt", "")).strip(),
                    f"{skill_dir.name}#{case_id}: behaviour_prompt duplicates prompt; it "
                    "exists to inline the material the prompt only names",
                )
                self.assertGreater(
                    len(behaviour),
                    len(str(case.get("prompt", "")).strip()),
                    f"{skill_dir.name}#{case_id}: behaviour_prompt is shorter than prompt; "
                    "inlining material makes it longer, so this one probably trimmed the "
                    "request instead of carrying its material",
                )
                self.assertNotRegex(
                    str(case.get("expected_output", "")),
                    r"(?i)^should\s+not\s+trigger",
                    f"{skill_dir.name}#{case_id}: negative cases are trigger-only; the "
                    "behaviour runner never reads them",
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

    def test_skill_content_carries_no_comments(self):
        # A skill file is loaded into a live context window, so a maintainer note
        # inside it is paid for by every session that triggers the skill and read
        # by nobody it was written for. Whether a given host strips HTML comments
        # is not a licence to add them: hosts differ, the same file ships to all of
        # them, and any of them may show the comment when the file is opened with a
        # read tool. Notes about a skill belong in this repository's README, which
        # no runtime loads. Code fences are exempt: a `#` there is sample code.
        for skill_dir in skill_dirs():
            paths = [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))]
            for path in paths:
                in_fence = False
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if line.lstrip().startswith("```"):
                        in_fence = not in_fence
                        continue
                    if in_fence:
                        continue
                    where = f"{path.relative_to(ROOT)}:{number}"
                    self.assertNotIn("<!--", line, f"{where} carries an HTML comment")
                    self.assertFalse(
                        line.lstrip().startswith("//"),
                        f"{where} carries a comment line: {line!r}",
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
                # here left Chinese triggering permanently untested. The same
                # carve-out covers `behaviour_prompt`, which restates one of
                # those prompts with its material inlined and is therefore in
                # the same language. Every other evals.json field stays English.
                payload = json.loads(text)
                fields = [str(payload.get("skill_name", ""))]
                for case in payload.get("evals", []):
                    fields.extend(
                        str(value)
                        for key, value in case.items()
                        if key not in ("prompt", "behaviour_prompt")
                    )
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


if __name__ == "__main__":
    unittest.main()
