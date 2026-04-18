from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LEGACY = load_module("legacy-component-skinning/scripts/build_surface_manifest.py")
XYLINK = load_module("xylink-legacy-component-skinning/scripts/build_surface_manifest.py")


class SurfaceManifestTests(unittest.TestCase):
    def test_manifest_includes_new_sections_and_checkpoints(self):
        markdown = LEGACY.build_markdown(
            page="Account Settings",
            route="/settings/account",
            composites=["toolbar"],
            interactions=[["click", "Edit", "drawer", "top-right action"]],
            exceptions=[["validation-error", "inline-form", "local submit", "password mismatch"]],
        )

        self.assertIn("## Content/Layout Cases", markdown)
        self.assertIn("## Breakpoint Coverage", markdown)
        self.assertIn("## Unverified Items", markdown)
        self.assertIn("## Exit Checklist", markdown)
        self.assertIn("| L1 |", markdown)
        self.assertIn("desktop=`TODO`", markdown)
        self.assertIn("- [ ] manifest updated with evidence or explicit unverified reasons", markdown)

    def test_manifest_defaults_include_layout_case_and_unverified_placeholder(self):
        markdown = XYLINK.build_markdown(
            page="Login",
            route=None,
            composites=[],
            interactions=[],
            exceptions=[],
        )

        self.assertIn("| L1 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |", markdown)
        self.assertIn("| B1 | desktop | TODO | TODO |", markdown)
        self.assertIn("| U1 | TODO | TODO | TODO |", markdown)


if __name__ == "__main__":
    unittest.main()
