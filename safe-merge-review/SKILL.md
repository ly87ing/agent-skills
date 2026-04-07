---
name: safe-merge-review
description: 在需要把一个分支、远程分支或一组相关仓库中的对应分支合并到当前工作分支时使用；也用于“检查 merge 是否正确”“确认是否漏合并”“审查 merge 冲突”“合并后复核逻辑是否错配”“决定是否可以 push”等场景。该 skill 强制执行合并前差异建模、热点重叠与语义冲突审查、分级 merge 策略、合并后完整性验证、逻辑错误复查、最小相关验证与 push 决策，目标是用证据证明合并正确，而不是只执行 git merge。
---

# Safe Merge Review

## Overview

把“Git merge 成功”和“合并结果正确”视为两件不同的事。先证明要合什么，再证明已经完整合进去，最后证明最终代码没有被错误拼接。

## Hard Gates

- 先 `fetch` 并锁定精确 ref，再讨论差异。
- 先检查工作区是否干净，再决定是否允许 merge。
- 先看 incoming commits、受影响文件和热点交集，再执行 merge。
- 当热点文件归属不明确时，先使用首选语义代码搜索工具定位真实 owner，再做精读；只对已知标识符和配置键使用精确 grep。
- 非平凡 merge 默认走“可审查 merge”路径；先审 staged 结果，再落最终 commit。
- 不把“没有文本冲突”当成“没有逻辑冲突”。
- 只有在来源 ref 被证明已经包含于 `HEAD` 后，才可宣称“已完整合并”。
- 未经过完整性验证、语义复查和最小相关验证，不默认允许 push。
- 任何 gate 被跳过，都必须显式说明跳过原因和剩余风险。

## Workflow

1. 识别仓库范围。
   - 判断当前请求覆盖单仓还是多仓。
   - 多仓场景逐仓处理，逐仓给证据，不合并成一句结论。
2. 稳定工作区。
   - 读取 `git status --short --branch`。
   - 对 dirty worktree 先判断是否与本次 merge 相关。
   - 默认停止并要求明确策略；不要静默把用户已有改动混进 merge 结果。
3. 锁定 ref 并获取最新远程状态。
   - 确认当前分支、来源 ref、目标 ref、remote。
   - 对来源分支执行 `fetch`，再做比较。
4. 建模差异集合。
   - 计算 merge base。
   - 统计左右独有提交数。
   - 拉出 incoming commits。
   - 建立双方自 merge base 以来的改动文件集合。
   - 当历史存在 rebase/改写嫌疑时，补做 patch-equivalent 检查，不把“提交号不同”直接当成“未合并”。
5. 识别热点重叠。
   - 优先找双方都改过的交集文件。
   - 对共享逻辑、公共接口、配置、schema、迁移、构建脚本、测试、生成物提级审查。
6. merge 前做语义审查。
   - 读热点代码和邻近测试。
   - 判断来源分支的新行为是否会被当前分支静默覆盖、部分采纳或接入不完整。
   - 使用 [references/merge-review-checklist.md](references/merge-review-checklist.md) 做强制复核。
7. 选择 merge 策略。
   - 使用 [references/merge-workflow.md](references/merge-workflow.md) 的策略矩阵。
   - 非平凡 merge 优先 `--no-ff --no-commit`，先审结果，再提交。
8. 用三方证据处理冲突。
   - 对每个冲突文件看 base、ours、theirs。
   - 不靠直觉拍板冲突解决结果。
9. merge 后证明“完整合并”。
   - 证明来源 ref 已被包含进 `HEAD`。
   - 证明 `HEAD..<source>` 为空。
   - 列出最终真正落地的文件与差异。
10. merge 后再次做语义复查。
    - 重点检查最终代码是否只是某一边逻辑误胜，而不是预期整合。
11. 运行最小相关验证。
    - 只跑最小但真正可能因为本次 merge 失败的验证命令。
12. 决定是否允许 push。
    - 只有用户要求 push 或仓库流程要求时才 push。
    - push 前再次确认工作区状态与验证结果。

## Required Output

每次 merge 结束都输出证据矩阵，至少包含：

- 仓库
- 当前分支
- 来源 ref
- merge base
- 左右独有提交数
- incoming 关键提交
- 热点交集文件
- 采用的 merge 策略
- 冲突文件及其处理依据
- 完整性验证结果
- 语义复查结论
- 运行的验证命令与结果
- 是否 push

## Escalate Risk

出现以下任一情况时，把 merge 视为高风险并加深审查：

- dirty worktree
- 多仓联动
- binary files、submodule、大量 rename
- 共享接口、schema、配置、迁移、打包或部署逻辑变更
- 测试被删除、禁用或大幅重写
- 来源分支存在 rebase、squash 或重写历史
- 生成物变化与源码变化不匹配

## References

- 读取 [references/merge-workflow.md](references/merge-workflow.md) 获取命令模板、策略矩阵与完整性验证方法。
- 在 merge 前后各读取一次 [references/merge-review-checklist.md](references/merge-review-checklist.md)，把逻辑正确性复查做成强制动作，而不是事后补充。
