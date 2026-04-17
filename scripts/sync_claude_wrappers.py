#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
SKILL_MD_PATTERN = re.compile(
    r"^---\nname:\s*(?P<name>.+)\ndescription:\s*(?P<description>.+)\n---\n",
    re.DOTALL,
)
TITLE_PATTERN = re.compile(r"^#\s+(?P<title>.+)$", re.MULTILINE)


def discover_canonical_skills() -> list[Path]:
    skills = []
    for path in sorted(REPO_ROOT.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith("."):
            continue
        skill_md = path / "SKILL.md"
        if skill_md.is_file():
            skills.append(skill_md)
    return skills


def parse_skill_metadata(skill_md: Path) -> tuple[str, str, str]:
    content = skill_md.read_text(encoding="utf-8")
    match = SKILL_MD_PATTERN.match(content)
    if not match:
        raise ValueError(f"无法解析 frontmatter: {skill_md}")
    title_match = TITLE_PATTERN.search(content)
    if not title_match:
        raise ValueError(f"无法解析标题: {skill_md}")
    return (
        match.group("name").strip(),
        match.group("description").strip(),
        title_match.group("title").strip(),
    )


def build_wrapper(name: str, description: str, title: str, canonical_dir_name: str) -> str:
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


def sync_wrappers(dry_run: bool) -> int:
    CLAUDE_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    generated = []
    for skill_md in discover_canonical_skills():
        name, description, title = parse_skill_metadata(skill_md)
        wrapper_dir = CLAUDE_SKILLS_DIR / skill_md.parent.name
        wrapper_md = wrapper_dir / "SKILL.md"
        content = build_wrapper(
            name=name,
            description=description,
            title=title,
            canonical_dir_name=skill_md.parent.name,
        )
        generated.append(wrapper_md)
        if dry_run:
            print(f"[DRY-RUN] would write {wrapper_md.relative_to(REPO_ROOT)}")
            continue
        wrapper_dir.mkdir(parents=True, exist_ok=True)
        wrapper_md.write_text(content, encoding="utf-8")
        print(f"[OK] wrote {wrapper_md.relative_to(REPO_ROOT)}")

    existing = {path for path in CLAUDE_SKILLS_DIR.glob("*/SKILL.md")}
    stale = sorted(existing - set(generated))
    for wrapper_md in stale:
        if dry_run:
            print(f"[DRY-RUN] would remove stale {wrapper_md.relative_to(REPO_ROOT)}")
            continue
        wrapper_md.unlink()
        wrapper_md.parent.rmdir()
        print(f"[OK] removed stale {wrapper_md.relative_to(REPO_ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Claude Code skill wrappers from canonical root skills.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing files.")
    args = parser.parse_args()
    return sync_wrappers(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
