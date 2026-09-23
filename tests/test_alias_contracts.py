"""Offline gates for the recommended terminal shortcuts in `aliases/`.

Agent Manager rejects an alias it cannot write safely, so a bad entry here would only show up as a
recommendation that fails to add; these checks catch it before it is pushed.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ALIASES = ROOT / "aliases"
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def alias_files():
    return sorted(ALIASES.glob("*.json"))


class AliasContractTests(unittest.TestCase):
    def test_every_file_has_the_shape_agent_manager_reads(self):
        self.assertTrue(alias_files())
        for path in alias_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, dict, path.name)
            self.assertIsInstance(data.get("aliases"), dict, f"{path.name}: needs an 'aliases' object")
            for field in ("timezone", "lang"):
                if field in data:
                    self.assertIsInstance(data[field], str, f"{path.name}: {field}")

    def test_names_and_values_can_be_written_safely(self):
        for path in alias_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            for name, value in data["aliases"].items():
                self.assertRegex(name, NAME, f"{path.name}: alias name {name!r}")
                self.assertIsInstance(value, str, f"{path.name}: {name}")
                self.assertTrue(value.strip(), f"{path.name}: {name} is empty")
                self.assertNotIn("'", value, f"{path.name}: {name} contains a single quote")
                self.assertNotIn("\n", value, f"{path.name}: {name} contains a newline")

    def test_defaults_carry_no_permission_skipping_flags(self):
        for path in alias_files():
            text = path.read_text(encoding="utf-8")
            for flag in ("--dangerously-skip-permissions", "--dangerously-bypass-approvals-and-sandbox"):
                self.assertNotIn(flag, text, f"{path.name}: {flag}")


if __name__ == "__main__":
    unittest.main()
