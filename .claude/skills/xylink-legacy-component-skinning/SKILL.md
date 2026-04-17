---
name: xylink-legacy-component-skinning
description: "当参考视觉规范明确来自 XYLINK UIKit demo，且需要在不替换 legacy 前端组件、不改 API / 数据流 / 业务逻辑的前提下，处理 XYLINK 风格迁移、交互后隐藏界面样式问题、异常态或降级态样式问题，以及换肤验收时使用。适用于用户给出 XYLINK demo URL、截图，或指出弹窗/配置页/异常提示等界面与 XYLINK 规范不一致的场景。"
---

# XYLINK Legacy Component Skinning

这个文件仅用于让 Claude Code 在项目内原生发现该 skill。

## Canonical Source

- 在执行前先读取 [../../../xylink-legacy-component-skinning/SKILL.md](../../../xylink-legacy-component-skinning/SKILL.md)。
- 将根目录 skill 目录视为唯一真源。
- 需要参考资料或脚本时，读取 canonical skill 目录下的 `references/` 与 `scripts/`，不要在 `.claude/skills/` 中维护第二份副本。

## Wrapper Rules

- 不在这个 wrapper 中重复维护完整 workflow。
- 如果 wrapper 与 canonical source 有任何不一致，以 canonical source 为准。
- 对外贡献或修改时，优先修改根目录 canonical skill，再同步 wrapper。
