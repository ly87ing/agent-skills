---
name: legacy-component-skinning
description: "当需要在不替换 legacy 前端组件、不改 API / 数据流 / 业务逻辑的前提下，处理参考视觉迁移、隐藏交互界面样式问题、异常态或降级态样式问题，以及换肤验收时使用。适用于用户提供参考站点、设计稿截图、组件规范文档或视觉契约包，并指出默认页、交互后弹窗/抽屉/二级面板、异常 banner / 表单报错 / 后端不可用提示等需要统一视觉的问题。"
---

# Legacy Component Skinning

这个文件仅用于让 Claude Code 在项目内原生发现该 skill。

## Canonical Source

- 在执行前先读取 [../../../legacy-component-skinning/SKILL.md](../../../legacy-component-skinning/SKILL.md)。
- 将根目录 skill 目录视为唯一真源。
- 需要参考资料或脚本时，读取 canonical skill 目录下的 `references/` 与 `scripts/`，不要在 `.claude/skills/` 中维护第二份副本。

## Wrapper Rules

- 不在这个 wrapper 中重复维护完整 workflow。
- 如果 wrapper 与 canonical source 有任何不一致，以 canonical source 为准。
- 对外贡献或修改时，优先修改根目录 canonical skill，再同步 wrapper。
