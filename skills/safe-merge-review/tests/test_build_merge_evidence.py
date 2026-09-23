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
import tempfile
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


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def init_repo(repo: Path) -> None:
    git(repo.parent, "init", "-b", "main", str(repo))
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "user.email", "test@example.com")
    (repo / "shared.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "shared.txt")
    git(repo, "commit", "-m", "base")


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


    def test_collect_derives_premerge_git_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            init_repo(repo)
            git(repo, "branch", "source")

            (repo / "shared.txt").write_text("main\n", encoding="utf-8")
            git(repo, "commit", "-am", "main change")
            git(repo, "checkout", "source")
            (repo / "shared.txt").write_text("source\n", encoding="utf-8")
            git(repo, "commit", "-am", "source change")
            git(repo, "checkout", "main")

            output = render("--collect", "--repo", str(repo), "--source-ref", "source")

        self.assertIn(f"- repo: {repo.resolve()}", output)
        self.assertIn("- current branch: main", output)
        self.assertIn("- source ref: source", output)
        self.assertIn("- left/right counts: 1\t1", output)
        self.assertIn("- dirty worktree status: clean", output)
        self.assertIn("source change", output)
        self.assertIn("- shared.txt", output)
        self.assertIn("- completeness proof: TODO", output)
        self.assertIn("- proof method: TODO", output)

    def test_collect_marks_contained_source_with_ancestry_proof(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            init_repo(repo)
            git(repo, "checkout", "-b", "source")
            (repo / "source.txt").write_text("source\n", encoding="utf-8")
            git(repo, "add", "source.txt")
            git(repo, "commit", "-m", "source change")
            git(repo, "checkout", "main")
            git(repo, "merge", "--ff-only", "source")

            output = render("--collect", "--repo", str(repo), "--source-ref", "source")

        self.assertIn("- proof method: is-ancestor", output)
        self.assertIn(
            "- completeness proof: source is an ancestor of HEAD and HEAD..source is empty",
            output,
        )

    def test_collect_rejects_unknown_source_ref(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            init_repo(repo)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--collect",
                    "--repo",
                    str(repo),
                    "--source-ref",
                    "missing",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source ref is not a commit", result.stderr)


    def test_collect_rejects_option_like_source_ref(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            init_repo(repo)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--collect",
                    "--repo",
                    str(repo),
                    "--source-ref=-fake",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source ref must not start with", result.stderr)


if __name__ == "__main__":
    unittest.main()
