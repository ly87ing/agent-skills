"""Offline gates for the always-on rules in `rules/`.

They restore the size and anchor checks that guarded the rule core before it moved here from
agent-manager; `rules/README.md` explains why each one exists.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
CORE = RULES / "core.md"
EVALS = RULES / "evals" / "core.json"

# round(len / 4) cap. Raise it only together with a line that passed the delete test, and lower
# it again when that line leaves; never raise it to make this test pass. Lowered 525 -> 270 on
# 2026-09-24: four lines had left since the cap was last set and it had not followed them down.
CORE_TOKEN_BUDGET = 270


class RuleContractTests(unittest.TestCase):
    def test_core_stays_within_budget(self):
        approx_tokens = round(len(CORE.read_text(encoding="utf-8")) / 4)
        self.assertLessEqual(approx_tokens, CORE_TOKEN_BUDGET, f"rules/core.md too large: ~{approx_tokens} tokens")

    def test_every_eval_anchor_matches_exactly_one_core_line(self):
        lines = CORE.read_text(encoding="utf-8").splitlines()
        rules = json.loads(EVALS.read_text(encoding="utf-8"))["rules"]
        self.assertTrue(rules)
        for rule in rules:
            hits = [line for line in lines if rule["anchor"] in line]
            self.assertEqual(len(hits), 1, f"{rule['id']}: anchor {rule['anchor']!r} matches {len(hits)} lines")

    def test_every_core_line_has_an_eval_rule(self):
        # The delete test decides what stays in core.md, and a line with no case can never be
        # put to it; three lines went untested for months that way.
        lines = [line for line in CORE.read_text(encoding="utf-8").splitlines() if line.strip()]
        anchors = [rule["anchor"] for rule in json.loads(EVALS.read_text(encoding="utf-8"))["rules"]]
        for line in lines:
            self.assertTrue(any(anchor in line for anchor in anchors), f"no eval rule covers: {line}")

    def test_core_carries_no_comments_and_no_skill_routing(self):
        text = CORE.read_text(encoding="utf-8")
        self.assertNotIn("<!--", text)
        self.assertIsNone(re.search(r"use the `[^`]+` skill", text), "skill routing lines were removed on 2026-09-21")

    def test_rule_templates_are_listed_deliberately(self):
        # Agent Manager offers every rules/*.md except README.md as a rule template, so a new file
        # here reaches users as a new template. Add it to this list on purpose.
        templates = sorted(path.name for path in RULES.glob("*.md") if path.name.lower() != "readme.md")
        self.assertEqual(templates, ["core.md"])


if __name__ == "__main__":
    unittest.main()
