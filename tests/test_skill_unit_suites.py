"""Run every skill's private unit-test suite (e.g. safe-merge-review/tests/).

Per-skill suites guard fragile script logic next to the script they test, but
top-level discovery never imports them (hyphenated skill directories are not
importable packages), so without this aggregator they exist yet never run.
This makes `python3 -m unittest discover -s tests` the single gate that runs
everything.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Suites are stdlib-only unit tests; generous headroom over their sub-second
# runtime so a slow machine never flakes the gate.
SUITE_TIMEOUT_SECONDS = 120


class PerSkillUnitSuiteTests(unittest.TestCase):
    def test_every_per_skill_suite_passes(self):
        suite_dirs = sorted(
            path / "tests"
            for path in (ROOT / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").exists() and (path / "tests").is_dir()
        )
        self.assertTrue(
            suite_dirs,
            "no per-skill tests/ directory found; if the last one was removed "
            "on purpose, delete this gate together with it",
        )
        for suite_dir in suite_dirs:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(suite_dir), "-t", str(suite_dir)],
                capture_output=True,
                text=True,
                timeout=SUITE_TIMEOUT_SECONDS,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"{suite_dir.relative_to(ROOT)} failed:\n{result.stdout}\n{result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
