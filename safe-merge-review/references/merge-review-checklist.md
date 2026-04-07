# Merge Review Checklist

## 目录

- 1. 使用时机
- 2. merge 前强制复核
- 3. 冲突解决复核
- 4. merge 后逻辑错误模式
- 5. 多仓联动复核
- 6. 完整性与收尾
- 7. 证据矩阵模板

## 1. 使用时机

这份清单要用两次：

- merge 前：判断是否值得直接 merge，还是必须先深读热点逻辑
- merge 后：判断最终结果是否“Git 成功但逻辑错配”

## 2. Merge 前强制复核

### 2.1 工作区与范围

- 当前 repo 是否干净？
- 是否还有用户未提交改动会污染 merge 证据？
- 请求是否覆盖多个 repo？如果是，是否已经逐仓拆开？

### 2.2 差异范围

- merge base 是否明确？
- incoming commits 是否真的需要进入当前分支？
- 是否存在 patch-equivalent 提交，被 rebase/squash 后看起来像“没合”？

### 2.3 热点交集

以下问题任一为“是”，就把该文件列为高风险：

- 双方都改了同一文件
- 双方改了同一类、同一方法、同一配置键
- 改动落在 shared util / adapter / base service
- 改动涉及公共接口、DTO、API contract
- 改动涉及 schema、migration、初始化、回填、回滚
- 改动涉及 build、packaging、deploy、CI
- 改动涉及 tests、fixtures、mock、snapshot

### 2.4 语义问题

对每个高风险文件至少回答：

- 当前分支在这里想保留什么？
- 来源分支在这里新增或修正了什么？
- 最终结果应该是叠加、取其一，还是重写？
- 如果只是简单保留 ours 或 theirs，会不会丢掉另一边真正需要的语义？

### 2.5 新增模式/类型/配置

当来源分支新增以下内容时，逐项检查闭环：

- 新模式、新开关、新 schema key
- 新数据库类型、新部署类型、新运行模式
- 新服务、新模块、新资源文件
- 新配置中心项、新默认值、新模板

必须追问：

- 默认资源是否同步？
- 初始化逻辑是否同步？
- 验证逻辑是否同步？
- 探活逻辑是否同步？
- 回滚/恢复逻辑是否同步？
- 测试是否同步？

## 3. 冲突解决复核

对每个冲突文件，记录：

- base 的旧行为
- ours 的改动目的
- theirs 的改动目的
- 最终保留方案
- 为什么这个方案不会丢掉另一侧的必要逻辑

常见错误：

- 只保留了冲突块里的文本，却没保留配套 import / registration / test
- 方法体合并了，但调用方、配置项、默认值没跟进
- 解决冲突后能编译，但运行时条件分支已经失真

## 4. Merge 后逻辑错误模式

merge 后重点排查以下模式：

### 4.1 外层判断被泛化，内层实现仍写死旧分支

典型特征：

- 外层从 `if ("distribute")` 变成 `if (clusterDeploy)`
- 但内部依然写死旧模式、旧服务名、旧配置键

### 4.2 新增模式支持，但默认资源未补齐

典型特征：

- 代码支持了新模式、新模板、新数据库类型
- 默认 JSON / YAML / ConfigMap / assets / template 并未同步

### 4.3 入口支持了新类型，但初始化链路不完整

典型特征：

- controller / service 接受了新类型
- 但初始化、回填、探活、状态同步、恢复、监控仍只支持旧类型

### 4.4 只合进了“部署动作”，没合进“配置闭环”

典型特征：

- 可以创建资源、起 Pod、发请求
- 但没有把关键配置回写到系统状态或配置中心

### 4.5 companion repo 或上游下游 repo 未同步

典型特征：

- 后端 contract 变了，但前端没跟
- 管理端改了流程，但基础设施 repo 没跟
- 一个 repo `Already up to date`，但另一 repo 真正有改动，最后仍被错误地统一口径汇报

### 4.6 测试与保护网变弱

典型特征：

- 测试被删除、降级、跳过
- 构建 gate、校验脚本、打包保护被移除
- smoke 变成不覆盖真实风险

## 5. 多仓联动复核

当前请求如果涉及“前后台”“主仓 + companion 仓”“多个独立 repo”，逐仓复核：

- 当前分支名是否一致
- 来源分支名是否一致
- 哪些仓真的有 incoming commits
- 哪些仓只是 up-to-date
- 哪些仓需要 merge，哪些仓不该创建空 merge commit
- 最终结论必须逐仓输出，不能用一句“都合好了”带过

## 6. 完整性与收尾

merge 后至少再确认一次：

- 来源 ref 已是 `HEAD` 的祖先
- `HEAD..<source-ref>` 为空
- 实际落地文件与预期文件一致
- 没有 conflict marker 残留
- 没有“以为合了其实没落到工作分支”的情况
- 最小相关验证已经执行
- 如果未验证，是否已明确说明

## 7. 证据矩阵模板

使用下面的模板输出最终结论：

| 项目 | 内容 |
| --- | --- |
| Repo | |
| Current branch | |
| Source ref | |
| Merge base | |
| Left/right counts | |
| Incoming key commits | |
| Hotspot overlap files | |
| Dirty worktree status | |
| Merge strategy | |
| Conflicted files | |
| Completeness proof | |
| Semantic review conclusion | |
| Verification command(s) | |
| Push status | |

判定规则建议：

- `Green`：完整性通过，语义复查通过，验证通过
- `Yellow`：merge 已完成，但有跳过项或残余风险
- `Red`：存在漏合并、逻辑错配、未解决冲突或验证失败
