#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
SKILL_MD_PATTERN = re.compile(
    r"^---\nname:\s*(?P<name>.+)\ndescription:\s*(?P<description>.+)\n---\n",
    re.DOTALL,
)
TITLE_PATTERN = re.compile(r"^#\s+(?P<title>.+)$", re.MULTILINE)


def parse_skill_metadata(path: Path) -> tuple[str, str, str]:
    content = path.read_text(encoding="utf-8")
    match = SKILL_MD_PATTERN.match(content)
    if not match:
        raise ValueError(f"无法解析 frontmatter: {path}")
    title_match = TITLE_PATTERN.search(content)
    if not title_match:
        raise ValueError(f"无法解析标题: {path}")
    return (
        match.group("name").strip(),
        match.group("description").strip(),
        title_match.group("title").strip(),
    )


def expected_wrapper_content(name: str, description: str, title: str, canonical_dir_name: str) -> str:
    canonical_ref = f"../../../{canonical_dir_name}/SKILL.md"
    return (
        f"---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"这个文件仅用于让 Claude Code 在项目内原生发现该 skill。\n\n"
        f"## Canonical Source\n\n"
        f"- 在执行前先读取 [{canonical_ref}]({canonical_ref})。\n"
        f"- 将根目录 skill 目录视为唯一真源。\n"
        f"- 需要参考资料或脚本时，读取 canonical skill 目录下的 `references/` 与 `scripts/`，不要在 `.claude/skills/` 中维护第二份副本。\n\n"
        f"## Wrapper Rules\n\n"
        f"- 不在这个 wrapper 中重复维护完整 workflow。\n"
        f"- 如果 wrapper 与 canonical source 有任何不一致，以 canonical source 为准。\n"
        f"- 对外贡献或修改时，优先修改根目录 canonical skill，再同步 wrapper。\n"
    )


def main() -> int:
    issues: list[str] = []
    canonical_dirs = []
    for path in sorted(REPO_ROOT.iterdir()):
        if not path.is_dir() or path.name.startswith("."):
            continue
        skill_md = path / "SKILL.md"
        if skill_md.is_file():
            canonical_dirs.append(path)

    for canonical_dir in canonical_dirs:
        canonical_skill_md = canonical_dir / "SKILL.md"
        name, description, title = parse_skill_metadata(canonical_skill_md)
        wrapper_md = CLAUDE_SKILLS_DIR / canonical_dir.name / "SKILL.md"
        if not wrapper_md.is_file():
            issues.append(f"缺少 wrapper: {wrapper_md.relative_to(REPO_ROOT)}")
            continue
        actual = wrapper_md.read_text(encoding="utf-8")
        expected = expected_wrapper_content(name, description, title, canonical_dir.name)
        if actual != expected:
            issues.append(f"wrapper 漂移: {wrapper_md.relative_to(REPO_ROOT)}")

    if CLAUDE_SKILLS_DIR.is_dir():
        expected_dirs = {path.name for path in canonical_dirs}
        actual_dirs = {path.name for path in CLAUDE_SKILLS_DIR.iterdir() if path.is_dir()}
        for extra in sorted(actual_dirs - expected_dirs):
            issues.append(f"存在多余 wrapper: .claude/skills/{extra}")

    if issues:
        for issue in issues:
            print(f"[FAIL] {issue}")
        print("Run: python3 scripts/sync_claude_wrappers.py")
        return 1

    print("Dual-native layout verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
