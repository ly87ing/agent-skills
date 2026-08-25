from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_svg.py"


def validate(source: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        svg = Path(temp_dir) / "diagram.svg"
        svg.write_text(source, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments, str(svg)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )


class ValidateSvgTests(unittest.TestCase):
    def test_accepts_local_marker_reference(self):
        result = validate(
            """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <defs><marker id="arrow"><path d="M0 0L5 2.5L0 5z"/></marker></defs>
  <path d="M0 25H90" marker-end="url(#arrow)"/>
</svg>"""
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ids=1", result.stdout)
        self.assertIn("local_refs=1", result.stdout)

    def test_rejects_missing_marker_reference(self):
        result = validate(
            """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <defs><marker id="arr"/></defs>
  <path d="M0 25H90" marker-end="url(#arrow)"/>
</svg>"""
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing referenced id: arrow", result.stderr)

    def test_rejects_duplicate_ids(self):
        result = validate(
            """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <g id="service"/><g id="service"/>
</svg>"""
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate id: service", result.stderr)

    def test_rejects_non_svg_root(self):
        result = validate('<html viewBox="0 0 100 50"/>')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root element is 'html', expected 'svg'", result.stderr)

    def test_rejects_missing_href_and_aria_references(self):
        result = validate(
            """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"
  aria-labelledby="title details">
  <title id="title">System</title><use href="#missing-node"/>
</svg>"""
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing referenced id: details", result.stderr)
        self.assertIn("missing referenced id: missing-node", result.stderr)

    def test_rejects_missing_or_invalid_viewbox(self):
        for source in (
            '<svg xmlns="http://www.w3.org/2000/svg"/>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 -1 10"/>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 wide 10"/>',
        ):
            with self.subTest(source=source):
                result = validate(source)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("viewBox must contain", result.stderr)

    def test_external_dependency_requires_explicit_opt_in(self):
        source = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <image href="https://example.com/diagram.png"/>
</svg>"""

        rejected = validate(source)
        accepted = validate(source, "--allow-external")

        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("non-local dependency requires --allow-external", rejected.stderr)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn("external_refs=1", accepted.stdout)

    def test_finds_external_resources_in_foreign_object_and_css_import(self):
        source = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <style>@import "https://example.com/theme.css";</style>
  <foreignObject><img xmlns="http://www.w3.org/1999/xhtml" src="image.png"/></foreignObject>
</svg>"""

        result = validate(source)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("https://example.com/theme.css", result.stderr)
        self.assertIn("image.png", result.stderr)

    def test_xml_stylesheet_dependency_requires_explicit_opt_in(self):
        source = """<?xml-stylesheet href="https://example.com/theme.css" type="text/css"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"/>"""

        rejected = validate(source)
        accepted = validate(source, "--allow-external")

        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("https://example.com/theme.css", rejected.stderr)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn("external_refs=1", accepted.stdout)

    def test_javascript_reference_is_always_rejected(self):
        source = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">
  <a href="javascript:alert(1)"><text>open</text></a>
</svg>"""

        result = validate(source, "--allow-external")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active reference is not allowed", result.stderr)

    def test_rejects_doctype_and_malformed_xml(self):
        doctype = validate(
            '<!DOCTYPE svg><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>'
        )
        malformed = validate('<svg viewBox="0 0 1 1">')

        self.assertNotEqual(doctype.returncode, 0)
        self.assertIn("DOCTYPE declarations are not allowed", doctype.stderr)
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("malformed XML", malformed.stderr)


if __name__ == "__main__":
    unittest.main()
