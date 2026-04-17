---
name: safe-merge-review
description: 在需要把一个分支、远程分支或一组相关仓库中的对应分支合并到当前工作分支时使用；也用于“检查 merge 是否正确”“确认是否漏合并”“审查 merge 冲突”“合并后复核逻辑是否错配”“决定是否可以 push”等场景。该 skill 强制执行合并前差异建模、热点重叠与语义冲突审查、分级 merge 策略、合并后完整性验证、逻辑错误复查、最小相关验证与 push 决策，目标是用证据证明合并正确，而不是只执行 git merge。
---

# Safe Merge Review

这个文件仅用于让 Claude Code 在项目内原生发现该 skill。

## Canonical Source

- 在执行前先读取 [../../../safe-merge-review/SKILL.md](../../../safe-merge-review/SKILL.md)。
- 将根目录 skill 目录视为唯一真源。
- 需要参考资料或脚本时，读取 canonical skill 目录下的 `references/` 与 `scripts/`，不要在 `.claude/skills/` 中维护第二份副本。

## Wrapper Rules

- 不在这个 wrapper 中重复维护完整 workflow。
- 如果 wrapper 与 canonical source 有任何不一致，以 canonical source 为准。
- 对外贡献或修改时，优先修改根目录 canonical skill，再同步 wrapper。
