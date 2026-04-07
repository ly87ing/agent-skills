# Merge Workflow

## 目录

- 1. 仓库范围与工作区洁净度
- 2. 锁定 ref 与获取最新状态
- 3. 差异建模与 patch-equivalent 检查
- 4. 热点交集文件识别
- 5. merge 策略矩阵
- 6. 冲突处理
- 7. 合并完整性验证
- 8. 最小相关验证与 push 决策

## 1. 仓库范围与工作区洁净度

单仓时，先确认当前目录确实是 git 仓库。多仓时，先识别本次请求覆盖哪些 repo，再逐仓执行同一流程。

基础命令：

```bash
git status --short --branch
git branch --show-current
git remote -v
```

dirty worktree 处理原则：

- `status` 干净：继续。
- `status` 不干净且与本次 merge 相关：默认停止，先和用户确认隔离策略。
- `status` 不干净但看起来无关：仍然先说明风险，再决定是否继续。
- 不要静默 stash、reset、checkout 覆盖用户原有改动。

如果需要判断 dirty 内容是否与 merge 相关，先看：

```bash
git diff --stat
git diff --cached --stat
```

## 2. 锁定 ref 与获取最新状态

不要使用模糊描述，例如“最新 master”或“远程那条线”。先把精确 ref 锁定出来。

常见命令：

```bash
git fetch origin <source-branch>
git rev-parse HEAD
git rev-parse <source-ref>
git rev-parse --abbrev-ref HEAD
```

如果请求是“把远程分支合到当前分支”，通常要先做：

```bash
git fetch origin <source-branch>
```

然后用 `origin/<source-branch>` 作为来源 ref，而不是本地过期分支名。

## 3. 差异建模与 patch-equivalent 检查

### 3.1 merge base

先求公共祖先：

```bash
git merge-base HEAD <source-ref>
```

这个结果决定后续所有“谁领先、谁落后、哪些文件重叠”的判断基准。

### 3.2 左右独有提交数

```bash
git rev-list --left-right --count HEAD...<source-ref>
```

解释：

- 左列：当前分支相对来源分支独有的提交数
- 右列：来源分支相对当前分支独有的提交数

### 3.3 incoming commits

先看来源分支真正新增了哪些提交：

```bash
git log --oneline HEAD..<source-ref>
```

再看两边补丁是否其实已等价存在：

```bash
git log --oneline --left-right --cherry-pick --no-merges HEAD...<source-ref>
```

当来源分支经历过 rebase、squash 或改写历史时，再补：

```bash
git range-diff "$(git merge-base HEAD <source-ref>)"..HEAD "$(git merge-base HEAD <source-ref>)"..<source-ref>
```

只有做过 patch-equivalent 检查后，才把“提交不存在”解释成“真的没合进去”。

## 4. 热点交集文件识别

先分别列出双方自 merge base 以来的改动文件：

```bash
BASE=$(git merge-base HEAD <source-ref>)
git diff --name-only "$BASE"..HEAD
git diff --name-only "$BASE"..<source-ref>
```

再求交集，重点审查双方都改过的文件。

如果 shell 环境允许，可用：

```bash
BASE=$(git merge-base HEAD <source-ref>)
git diff --name-only "$BASE"..HEAD | sort -u > /tmp/current.files
git diff --name-only "$BASE"..<source-ref> | sort -u > /tmp/source.files
comm -12 /tmp/current.files /tmp/source.files
```

优先审查以下交集：

- 共享 service / util / adapter
- controller 与 API contract
- 配置、schema、迁移、初始化逻辑
- build、packaging、deploy、CI 脚本
- 测试和测试夹具
- 生成物与其源文件

## 5. Merge 策略矩阵

### 5.1 来源已完全包含于当前分支

如果：

```bash
git merge-base --is-ancestor <source-ref> HEAD
```

返回成功，说明来源已经被包含。不要再执行 merge；直接报告 `Already contained / up to date`。

### 5.2 当前分支是来源分支祖先

如果：

```bash
git merge-base --is-ancestor HEAD <source-ref>
```

返回成功，说明这是 fast-forward 候选。

推荐流程：

1. 先完成 incoming commits、文件清单和语义审查。
2. 再根据仓库历史策略二选一：

```bash
git merge --ff-only <source-ref>
```

或

```bash
git merge --no-ff --no-commit <source-ref>
```

如果需要保留明确 merge 证据或先看 staged 结果，优先第二种。

### 5.3 真正的非平凡 merge

默认先用：

```bash
git merge --no-ff --no-commit <source-ref>
```

先检查 staged 结果：

```bash
git diff --cached --stat
git diff --cached --name-only
git diff --cached
```

确认结果正确后，再创建最终 merge commit。

不要把 `git merge --no-edit <source-ref>` 当成默认路径，除非你已经证明这是低风险、低歧义的 trivial merge。

## 6. 冲突处理

出现冲突时，先定位文件：

```bash
git diff --name-only --diff-filter=U
git ls-files -u
```

再分别看三方内容：

```bash
git show :1:path/to/file
git show :2:path/to/file
git show :3:path/to/file
```

含义：

- `:1:` base
- `:2:` ours
- `:3:` theirs

冲突处理规则：

- 先说明 base 上原来是什么。
- 再说明当前分支改了什么。
- 再说明来源分支改了什么。
- 最终结果必须能解释为什么保留、合并或舍弃某一侧逻辑。

在解决后，额外检查：

```bash
git diff --check
```

用于发现残留 conflict marker、空白错误等问题。

## 7. 合并完整性验证

在真正宣称“已合并”前，至少给出以下证据。

### 7.1 merge commit 或合并结果快照

如果已提交 merge commit：

```bash
git show --no-patch --pretty=raw HEAD
git show --stat --oneline -1
```

如果还是 `--no-commit` 状态：

```bash
git diff --cached --stat
git diff --cached --name-only
```

### 7.2 来源 ref 已被包含

```bash
git merge-base --is-ancestor <source-ref> HEAD
```

必须成功。

### 7.3 不存在剩余 incoming commits

```bash
git log --oneline HEAD..<source-ref>
```

必须为空。

### 7.4 实际落地文件与预期文件对齐

至少查看：

```bash
git diff --stat HEAD^1 HEAD
git diff --name-only HEAD^1 HEAD
```

或对 fast-forward merge 保存前置提交：

```bash
PRE_MERGE_HEAD=$(git rev-parse HEAD)
git merge --ff-only <source-ref>
git diff --stat "$PRE_MERGE_HEAD"..HEAD
git diff --name-only "$PRE_MERGE_HEAD"..HEAD
```

如果是多仓 merge，要逐仓做这一步。

## 8. 最小相关验证与 push 决策

根据实际改动选择最小但真实可失败的验证：

- Java 代码：`compileJava`、相关单测、模块测试
- 前端代码：相关测试、构建、局部 smoke
- 配置/脚本：执行对应检查或 dry-run
- 多仓联动：逐仓验证，再给总结果

验证后，再看一次：

```bash
git status --short --branch
```

只有在以下条件同时满足时，才可建议或执行 push：

- 来源 ref 已完整包含
- merge 后语义复查通过
- 最小相关验证通过
- 用户要求 push，或仓库流程明确要求继续 push
