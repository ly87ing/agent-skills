## Goal

把 `legacy-component-skinning` 与 `xylink-legacy-component-skinning` 的默认执行路径收敛为“先实施、后验收”，避免用户只是在做 skinning 时，agent 被 `review`、`acceptance`、`diff` 等词带进 git 审查流程。

## Decisions

- 默认请求走 `Path 1 + Path 2`，必要时补参考包，但不自动进入 `Path 3`
- 只有用户显式要求“验收 / review / 审查 / 检查当前改动”或直接提供当前 `diff` 时，才进入 `Path 3`
- 默认禁止查看 `git history / git log / branch / commit`；显式审查时最多查看当前相关 `diff`
- 隐藏 surface 与异常态问题默认属于实施范围，不因为“回看”字样自动升级为审查任务

## File Scope

- `legacy-component-skinning/SKILL.md`
- `legacy-component-skinning/agents/openai.yaml`
- `legacy-component-skinning/evals/evals.json`
- `xylink-legacy-component-skinning/SKILL.md`
- `xylink-legacy-component-skinning/agents/openai.yaml`
- `xylink-legacy-component-skinning/evals/evals.json`

## Verification

- 用 `rg` 复查 `acceptance review`、`git history`、`git log` 等误导性表述
- 用 `python3 -m json.tool` 校验两个 `evals.json`
