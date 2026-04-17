## Goal

把“内容可读优先，但不允许无限拉长”的平衡规则写入 skinning skill，避免 agent 只会修“过窄”问题，却忽略结构预算、同排节奏和视口约束。

## Decisions

- 把规则命名为 `Content Capacity Rules`，同时进入实施路径与验收路径
- 明确区分 `primary content`、`secondary content`、`overflow content`
- 默认扩容顺序固定为：合理 `min-width` -> 局部增宽 -> `panel` 宽于 `trigger` -> 最多 2 行 `wrap` -> `ellipsis`
- `tooltip` 只能作为补充，不得作为被截断内容的唯一主路径
- 对 `dropdown / select / cascader / autocomplete / segmented rail` 显式加约束，避免既过窄又过长

## File Scope

- `legacy-component-skinning/SKILL.md`
- `xylink-legacy-component-skinning/SKILL.md`
- `legacy-component-skinning/references/component-visual-contract-template.md`
- `legacy-component-skinning/references/visual-acceptance-checklist.md`
- `legacy-component-skinning/evals/evals.json`
- `xylink-legacy-component-skinning/evals/evals.json`

## Verification

- 用 `python3 -m json.tool` 校验两个 `evals.json`
- 用 `rg` 复查 `Content Capacity Rules`、`ellipsis`、`tooltip` 等关键约束是否已进入 core 和 profile
