# agent-skills

面向 Codex、Claude Code、Antigravity CLI 等 agent runtime 的开源通用 skill 集合，强调自然语言触发、闭环 workflow、可验证证据和可复用资源。

## 项目定位

这个仓库收集的是可直接复用的 `SKILL.md` 包，而不是零散提示词。

目标是把高频、易出错、需要稳定执行的工程工作流沉淀成团队可复用的 skill：

- 有清晰的触发条件
- 有最小上下文要求
- 有可执行的 workflow
- 有验证与失败边界
- 有可下沉的 `references/` 与 `scripts/`

如果一个 skill 只能回答“怎么做”，却不能稳定把任务做完、验完、报完，这类内容不属于这个仓库的目标形态。

## 当前收录

| Skill | 说明 |
| --- | --- |
| [safe-merge-review](./safe-merge-review/SKILL.md) | 把“merge 成功”和“merge 正确”分开处理，强调差异建模、热点交集审查、完整性验证和 push 决策。 |
| [fix-ones-bug](./fix-ones-bug/SKILL.md) | 批量处理“一个负责人 × 一个迭代/版本”的 ONES 缺陷，覆盖排查、修复、回归、证据和流转。 |
| [qa-self-verify](./qa-self-verify/SKILL.md) | 在真实 QA/远端环境批量自验证已修复缺陷，采集 UI 证据并回填 ONES，不写代码。 |
| [architecture-change-review](./architecture-change-review/SKILL.md) | 在修改架构、接口、依赖边界、配置 schema 或跨模块契约前做边界复核。 |
| [code-style-contracts](./code-style-contracts/SKILL.md) | 处理代码风格、配置、数据契约、命名、校验和注释约束，避免把规则细节塞进 always-on 上下文。 |
| [frontend-verification](./frontend-verification/SKILL.md) | 处理 UI、浏览器自动化、交互 HTML、响应式状态和前端验证工具选择。 |
| [artifact-hygiene](./artifact-hygiene/SKILL.md) | 判断生成文件、调试产物、Playwright 证据、下载件和临时脚本的放置与清理边界。 |
| [reader-facing-writing](./reader-facing-writing/SKILL.md) | 编写或改写面向读者的计划、报告、提案、规格、清单、Markdown 和 HTML 文档。 |

## 设计原则

- 证据优先：不靠猜测下结论，必须说明验证方式与结果。
- 闭环优先：从触发、上下文、执行、验证到汇报形成完整路径。
- 共享优先：可复用规则应下沉到共享层，而不是散落在页面补丁或临时说明里。
- 工具中立：强制真实观察效果，但不强绑某一个具体工具。
- 安全边界明确：什么时候可以自动执行，什么时候必须停下并升级，要写清楚。
- 渐进加载：`SKILL.md` 保持精炼，细节下沉到 `references/`，脆弱步骤尽量下沉到 `scripts/`。

## 仓库结构

```text
agent-skills/
├── safe-merge-review/
│   ├── SKILL.md                        # runtime-neutral source
│   ├── agents/
│   │   ├── openai.yaml                 # Codex/OpenAI UI metadata
│   │   ├── codex.md                    # Codex tool mapping notes
│   │   ├── claude.md                   # Claude Code tool mapping notes
│   │   └── antigravity.md              # Antigravity CLI tool mapping notes
│   └── references/
├── fix-ones-bug/
│   ├── SKILL.md
│   ├── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
│   └── references/
├── qa-self-verify/
│   ├── SKILL.md
│   ├── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
│   ├── references/
│   └── scripts/
├── architecture-change-review/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
├── code-style-contracts/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
├── frontend-verification/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
├── artifact-hygiene/
│   ├── SKILL.md
│   └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
└── reader-facing-writing/
    ├── SKILL.md
    └── agents/{openai.yaml,codex.md,claude.md,antigravity.md}
```

根目录 skill 目录就是唯一真源，也是这个仓库公开维护的唯一内容层。

每个 canonical skill 目录都应尽量自包含，通常包括：

- `SKILL.md`：跨运行时触发条件与主 workflow，保持 open-standard 和 runtime-neutral
- `agents/openai.yaml`：Codex/OpenAI UI 元数据与默认调用提示
- `agents/codex.md`：Codex 工具映射、进度跟踪和验证入口的薄适配说明
- `agents/claude.md`：Claude Code 命令、工具映射和安全注意事项的薄适配说明
- `agents/antigravity.md`：Antigravity CLI 调用方式、进度跟踪和工具边界的薄适配说明
- `references/`：按需加载的参考资料（单文件超过 100 行时在顶部放一份目录，保证部分读取也能看到全貌）
- `scripts/`：适合沉淀为 deterministic helper 的脆弱步骤
- `evals/evals.json`：触发判别与行为评估用例，正例覆盖 `description` 的触发场景、反例防误触发或确认路由到兄弟 skill

当前 8 个 skill 均已附带 `evals/evals.json`，对齐 Anthropic「先建评估」的 skill authoring 实践。

运行时适配规则：

- `SKILL.md` 是唯一 workflow 真源；adapter 只能映射工具、调用方式和运行时安全限制。
- Codex/OpenAI 专属配置放在 `agents/openai.yaml`，并让 `default_prompt` 显式引用 `$skill-name`。
- Claude Code 专属调用方式、工具名、动态上下文注入限制放在 `agents/claude.md`，不写进 core。
- Codex 专属工具习惯（如计划跟踪、本地浏览器选择、图片查看方式）放在 `agents/codex.md`，不写进 core。
- Antigravity CLI 专属调用方式、计划 / 状态表面和工具边界放在 `agents/antigravity.md`，不写进 core。
- adapter 不允许新增、删除或放宽 `SKILL.md` 里的验证 gate、停止条件和状态流转要求。

## 如何使用

你不需要采用某个固定安装器；这个仓库更强调 skill 包本身的可移植性。

常见用法：

1. 选择需要的 skill 目录。
2. 把该目录复制到你的 agent skills 路径，或作为子目录 / 子模块引入自己的仓库。
3. 确保运行时能够发现 `SKILL.md`。
4. 让 agent 按 skill 的自然语言触发条件调用，必要时按需读取 `references/` 或运行 `scripts/`。

这个仓库本身保持 runtime-neutral，不在仓库里额外维护 Claude Code、Codex 或 Antigravity CLI 的项目级 wrapper。
如果你要在某个具体运行时里使用这些 skill，应由消费侧把 skill 放到该运行时要求的发现路径中。

从规则体系拆出来的 skill 应只承载低频、专题化、需要按需加载的 workflow。Always-on 规则只保留触发条件、约束边界和最小协作协议；执行步骤、检查清单、失败边界和验证细节放在对应 skill 中维护。

## 适合放进这个仓库的 skill

- 团队会重复遇到的工程工作流
- 单靠口头说明很容易走偏的任务
- 需要明确失败边界、升级条件和验证证据的任务
- 能把重复步骤沉淀为 `references/` 或 `scripts/` 的任务

## 不适合放进这个仓库的内容

- 一次性项目说明
- 只适用于单个仓库、且无法抽象复用的内部约定
- 只有概念建议、没有执行闭环的长文档
- 本来更适合做成 lint / script / CI 校验的机械规则

## 贡献建议

- 一个 skill 一个目录，命名尽量清晰直接。
- `SKILL.md` 只保留核心 workflow，不把 README、CHANGELOG、安装说明塞进 skill 包里。
- 重复且脆弱的步骤优先下沉到 `scripts/`，不要一遍遍用 prose 复述。
- 触发条件要写给真实用户请求，而不是写成抽象口号。
- 同时适配 Claude Code、Codex 和 Antigravity CLI 时，保持 `SKILL.md` open-standard，把运行时差异收敛到 `agents/` adapter。
- 如果 skill 面向团队重复使用，至少要能回答：
  - 谁会用
  - 用户会怎么触发
  - 执行前最少要收集什么上下文
  - 怎样证明任务真的完成
  - 什么时候必须停止或升级

如果你使用 Codex 的 `skill-creator` 系工具链，建议在提交前补一次结构校验和 team audit。

## 项目描述建议

适合放在 GitHub 仓库设置页的简短描述：

`Open-source, team-grade skills for safe merges, rule-derived workflows, and reusable agent execution.`
