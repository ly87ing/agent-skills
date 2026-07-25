"""Guard the evidence renderer's placeholders.

The renderer produces the artifact a reviewer reads as proof, so an unfilled
field must look unfilled. The regression this pins: proof method used to
default to "is-ancestor", so a summary built without ever running a
completeness check still claimed the strongest proof — and is-ancestor is
precisely the method that does not hold for a squash merge.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_merge_evidence.py"


def render(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise AssertionError(f"exit {result.returncode}: {result.stderr}")
    return result.stdout


class BuildMergeEvidenceTests(unittest.TestCase):
    def test_unset_proof_method_stays_unfilled(self):
        output = render("--repo", "demo")

        self.assertIn("- proof method: TODO", output)
        self.assertNotIn("is-ancestor", output)

    def test_recorded_fields_render_verbatim(self):
        output = render(
            "--repo",
            "demo",
            "--proof-method",
            "patch-equivalent",
            "--hotspot",
            "src/app/config.py",
            "--hotspot",
            "build.gradle",
        )

        self.assertIn("- repo: demo", output)
        self.assertIn("- proof method: patch-equivalent", output)
        self.assertIn("- src/app/config.py", output)
        self.assertIn("- build.gradle", output)

    def test_unset_scalars_and_lists_are_visibly_missing(self):
        output = render("--repo", "demo")

        self.assertIn("- completeness proof: TODO", output)
        self.assertIn("- semantic review conclusion: TODO", output)
        # Residual risks are the one list whose emptiness is a real answer.
        self.assertIn("- none recorded", output)

    def test_invalid_proof_method_is_rejected(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--proof-method", "looks-fine-to-me"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
