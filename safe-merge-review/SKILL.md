---
name: safe-merge-review
description: 在用户要把一个 branch、remote ref 或一组相关仓库中的对应分支合并到当前工作分支，或要复核“这个 merge 是否正确”“是否漏合并”“冲突处理是否可靠”“merge 后能不能 push”时使用。适用于用户提供 branch name、remote ref、repo path、冲突文件、merge commit、merge request 链接或多仓分支集合的场景。通过差异建模、热点交集审查、语义复查、完整性证明、最小相关验证和 push 决策，证明“merge 正确”，而不只是执行 git merge。
---

# Safe Merge Review

## Outcome

把“merge 成功”和“merge 正确”视为两件不同的事，并输出可核对证据：

- 当前 merge 覆盖哪些 repo、哪些 ref
- 来源改动是否真的需要进入当前分支
- 哪些热点文件和共享边界需要深读
- 冲突处理是否保留了双方必要语义
- 来源 ref 是否已被完整包含进 `HEAD`
- 最小相关验证是否通过
- 当前结果是否允许 push，以及剩余风险是什么

## Roles and Jobs

- Engineering:
  - 把来源分支安全合到当前分支
  - 复核 merge 结果是否存在逻辑错配、漏合并或错误取舍
- Release / QA:
  - 判断某次 merge 是否具备继续验证、提测或 push 的条件
  - 对多仓联动 merge 做逐仓证据核对

## Trigger Matrix

| Trigger | Role | Required context | Path |
| --- | --- | --- | --- |
| “把 `feature/foo` merge 到当前分支” | Engineering | repo path + source ref | 路径 1 + 路径 2 |
| “检查这个 merge 有没有漏掉东西” | Engineering / QA | repo path + source ref 或 merge commit | 路径 1 + 路径 3 |
| “这个冲突该怎么解，解完能不能 push” | Engineering | repo path + conflicted files + source ref | 路径 1 + 路径 2 |
| “这几个仓的对应分支都要合一下，帮我确认是否正确” | Release / Engineering | repo list + source refs | 路径 1 + 路径 2 |
| “这个分支看起来已经 merge 了，帮我证明是否真的包含了” | Engineering / QA | repo path + source ref 或 merge commit | 路径 3 |

## Context Sources

开始执行前先收齐最小上下文：

- 仓库范围：
  - 当前目录是否为 git repo
  - 单仓还是多仓
  - 当前分支、目标分支、来源 ref、remote
- 工作区状态：
  - `git status --short --branch`
  - 是否存在未提交改动、暂存改动或用户手工冲突解决现场
- merge 证据：
  - 来源 ref 或 merge commit
  - 受影响文件、热点交集、关键 incoming commits
  - 仓库是否有 fast-forward、merge commit、squash 等历史策略
- 验证上下文：
  - 最小相关验证命令
  - 是否需要逐仓分别验证
- 风险边界：
  - 是否存在 dirty worktree、多仓联动、submodule、binary files、大量 rename、rebase/squash 历史
  - 是否需要联网 `fetch`

环境前提：

- 需要可用的 git CLI 和仓库读写权限
- 判断远程来源 ref 时通常需要联网 `fetch`

## Reference Loading Guide

按需读取资料，而不是一次性把全部细节塞进主流程：

- 需要命令模板、策略矩阵、patch-equivalent 或完整性校验方法时，读取 [references/merge-workflow.md](references/merge-workflow.md)
- 需要判断热点风险、冲突语义或 merge 后逻辑错配模式时，读取 [references/merge-review-checklist.md](references/merge-review-checklist.md)
- 需要生成稳定的汇报骨架时，运行 [scripts/build_merge_evidence.py](scripts/build_merge_evidence.py)

## Workflow Paths

### Path 1: 建模并决定 merge 方案

1. 稳定工作区。
   - 先看 `git status --short --branch`
   - dirty worktree 默认不直接 merge；先说明风险，再决定是否继续
2. 锁定来源与目标 ref。
   - 明确当前分支、来源 ref、目标 ref、remote
   - 来源 ref 不清时，不猜测“最新那条线”
3. 获取最新状态并建模差异。
   - 优先按 [references/merge-workflow.md](references/merge-workflow.md) 执行 `fetch`、merge base、left/right counts、incoming commits、文件集合比较
   - 历史存在 rebase / squash / 改写嫌疑时，补做 patch-equivalent 检查
4. 识别热点交集并做语义预审。
   - 优先审查双方都改过的共享逻辑、公共接口、配置、schema、迁移、构建脚本、测试和生成物
   - 对高风险文件按 [references/merge-review-checklist.md](references/merge-review-checklist.md) 逐项复核
5. 选择 merge 策略。
   - 来源已被包含时，直接报告 `already contained`
   - 非平凡 merge 默认走可审查路径，先看 staged 结果，再落最终 commit

### Path 2: 执行 merge 并证明结果正确

1. 执行已选 merge 策略。
   - fast-forward 候选也先完成差异建模和语义预审
   - 非平凡 merge 默认先审 staged 结果，不把“没有文本冲突”当成“没有逻辑冲突”
2. 用三方证据处理冲突。
   - 对每个冲突文件看 base / ours / theirs
   - 记录最终保留方案以及为什么没有丢失另一侧必要语义
3. 证明“完整合并”。
   - 证明来源 ref 已被包含于 `HEAD`
   - 证明 `HEAD..<source-ref>` 为空
   - 列出最终真正落地的文件与差异
4. 再做一次 merge 后语义复查。
   - 检查最终代码是否只是某一边逻辑误胜
   - 重点看共享边界、初始化链路、配置闭环、默认资源、上下游仓库联动
5. 运行最小相关验证。
   - 只跑真正可能因为本次 merge 失败的验证命令
   - 多仓场景逐仓记录，不合并成一句“都过了”
6. 决定是否允许 push。
   - 只有用户明确要求 push 或流程明确要求时才 push
   - 任一 gate 被跳过，必须显式写明原因和剩余风险

### Path 3: 审计已完成的 merge

1. 锁定审计对象。
   - 明确是审某个 merge commit、某个来源 ref，还是当前工作树结果
2. 重建预期差异。
   - 重新计算 merge base、incoming commits、文件集合和热点交集
   - 不把“现在看起来没差异”直接等同于“当时合得对”
3. 检查完整性与语义。
   - 对照来源 ref、落地文件和最终代码
   - 重点排查 [references/merge-review-checklist.md](references/merge-review-checklist.md) 里的 merge 后错误模式
4. 运行最小相关验证并输出结论。
   - 结论只能是 `Green / Yellow / Red`
   - 必须带证据矩阵和剩余风险

## Reusable Resources

### scripts/

- [scripts/build_merge_evidence.py](scripts/build_merge_evidence.py)
  生成稳定的 merge evidence Markdown 骨架，用于多仓或高风险 merge 的统一汇报。适合在 ref 已锁定、风险项已识别后运行，避免每次手工拼接字段导致证据漂移。

### references/

- [references/merge-workflow.md](references/merge-workflow.md)
  读取命令模板、策略矩阵、冲突处理方法和完整性验证方法。
- [references/merge-review-checklist.md](references/merge-review-checklist.md)
  读取热点风险、语义问题、merge 后逻辑错误模式和证据矩阵模板。

## Verification Matrix

| Path | Check | Evidence |
| --- | --- | --- |
| 路径 1 | 来源与目标 ref 已锁定，差异集合和热点文件已建模 | merge base、left/right counts、incoming commits、热点文件列表 |
| 路径 2 | merge 结果被完整包含且最小相关验证完成 | 完整性证明、最终落地文件、验证命令与结果、push 决策 |
| 路径 3 | 已完成 merge 的正确性被重新审计 | 来源 ref / merge commit、语义复查结论、验证结果、Green/Yellow/Red 判定 |

## Failure and Escalation

遇到以下情况时停止或升级，而不是继续猜：

- 来源 ref、目标 ref、remote 不明确
- dirty worktree 会污染 merge 证据，但用户尚未确认处理策略
- 无法 `fetch` 最新来源状态，却仍需要判断远程分支
- 需要 `reset`、`checkout --`、强制覆盖冲突结果等破坏性动作，但用户尚未批准
- 多仓联动中有仓缺少上下文、缺少来源 ref 或缺少验证命令
- 无法提供最小相关验证，只能给出“未验证”而不能宣称完成

## Reporting

完成后至少汇报以下内容：

### Safe merge review summary
- repo:
- current branch:
- source ref:
- merge base:
- left/right counts:
- incoming key commits:
- hotspot overlap files:
- merge strategy:
- conflicted files and reasoning:
- completeness proof:
- semantic review conclusion:
- verification command(s):
- push status:
- residual risks:

如果是多仓场景，逐仓输出，不用一句“都合好了”替代。
