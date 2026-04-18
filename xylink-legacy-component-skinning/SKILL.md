---
name: xylink-legacy-component-skinning
description: Use when legacy UI must align to XYLINK UIKit without replacing existing components, especially when hidden interactive surfaces, deep edit/detail flows, degraded states, or content/layout regressions need review or repair.
---

# XYLINK Legacy Component Skinning

## Outcome

把 XYLINK UIKit demo 当作视觉样例库，而不是实现来源，在不替换 legacy 组件的前提下完成可核对的 skinning：

- 明确使用了哪些 XYLINK 参考截图和关键状态
- 明确哪些共享层覆盖和页面补丁被实现
- 明确哪些复合业务场景、隐藏 surface 和异常态已被实际回看
- 明确哪些编辑链路、step、二级页面和内容布局问题已被实际回看
- 明确哪些差异来自 legacy 组件能力限制
- 明确没有复制 XYLINK 源码、构建产物或运行时资源

这个 profile 必须自包含执行；不要假设 sibling core skill 已安装。

## Roles and Jobs

- Engineering:
  - 让 legacy 组件视觉贴近 XYLINK UIKit，同时保留原组件与原行为
  - 审查实现是否越过非 UI 边界，或错误复制了 XYLINK 资源
- QA / Design:
  - 用 XYLINK 参考图和 demo 实际渲染结果做对照验收
  - 标记仍未向 XYLINK 新规范收敛的组件状态和业务场景

## Trigger Matrix

| Trigger | Role | Required context | Path |
| --- | --- | --- | --- |
| “按 XYLINK UIKit demo 给旧页面换肤” | Engineering | 宿主项目 + XYLINK 参考源 | 路径 1 + 路径 2 |
| “不要换组件，只把视觉往 XYLINK 靠” | Engineering | 目标页面 + XYLINK 参考图 | 路径 1 + 路径 2 |
| “默认页像了，但点开后的弹窗/高级区还是旧皮肤” | Engineering / QA | 可运行页面 + 交互入口 | 路径 2，必要时路径 3 |
| “编辑后打开的二级页面 / step / 二次确认弹窗也要按 XYLINK 一起看” | Engineering / QA | 可运行页面 + 编辑链路说明 | 路径 2，必要时路径 3 |
| “异常 banner、登录失败提示、后端不可用提示和 XYLINK 不一致” | Engineering / QA | 可运行页面 + 异常态复现条件 | 路径 2，必要时路径 3 |
| “检查这次改动有没有照搬 XYLINK 实现” | Engineering / QA | 当前 diff + XYLINK 参考截图 | 路径 3 |

## Route Selection Rules

- 默认把“换肤、补隐藏 surface、补异常态、修交互后样式”视为实施请求：先走路径 1（参考不足时）和路径 2，不要自动进入路径 3。
- 只有用户明确要求“验收 / review / 审查 / 检查当前改动 / 提供 diff”，或已经直接给出当前相关 diff 时，才进入路径 3。
- 默认不要查看 `git history`、`git log`、分支列表或提交记录。若路径 3 需要代码证据，只允许查看当前工作区相关 diff；除非用户明确要求历史审查，否则不要扩展到历史记录。
- 隐藏 surface 和异常态即使带有“回看”“检查”等字样，也默认先按实施问题处理；只有用户明确要求验收结论时，才补路径 3。

## Mandatory Gates

- 只要页面存在编辑、详情、step、二级路由、tab panel、row action、hover/focus reveal 等会打开新 surface 的入口，就必须先枚举这些入口，再声称“已检查”。
- 只要页面承载真实业务内容，就必须把 `content / layout` 作为 XYLINK 风格迁移的一等验收项，而不是只看颜色、边框和圆角。
- 只要存在无法真实查看的页面、状态、断点或异常态，就必须在 manifest 或最终汇报里明确标为 `unverified`；没有真实渲染证据时，不得给出“已向 XYLINK 收敛 / 已通过”的确定性结论。
- 只要存在多页面、深层编辑链路、内容承载风险或异常态，就必须生成并更新 surface manifest；manifest 未补证据或未写清未验证原因时，不得宣称完成。
- 默认优先复用共享层；只有当修复确实是页面特有结构差异、一次性场景，或下沉会引入错误耦合时，才允许局部实现，并且必须记录原因。

## Content Capacity Rules

- 关键内容可读优先，但受结构预算约束；不允许为了展示全文无限拉长控件、打散布局节奏或破坏整体层级。
- `primary content`（已选值、选项主文案、字段 label、error 核心信息）必须直接可读；`secondary content` 可在不破坏结构的前提下受限展示。
- `overflow content` 必须有稳定的补充查看路径；`tooltip` 只能补充，不能是唯一主路径。
- 默认扩容顺序：合理 `min-width` -> 局部增宽 -> `panel` 宽于 `trigger` -> 最多 2 行 `wrap` -> `ellipsis`。
- 只有当继续增宽或继续换行会明显破坏整体结构时，才允许 `ellipsis`。

## Context Sources

开始执行前先收齐最小上下文：

- XYLINK 参考侧：
  - XYLINK UIKit demo URL 或等价截图包
  - 关键组件状态截图
  - 真实业务复合场景截图
- 宿主项目：
  - 样式入口、共享组件目录、目标页面 / 路由、本地运行方式
  - 所有会改变可见 UI 的关键交互触发器
  - 可复现的异常态入口
- 验证环境：
  - 真实查看效果的手段，例如浏览器、DevTools、Playwright、录屏回传或人工截图
  - 目标项目已有的最小测试或 smoke 命令
  - 需要覆盖的断点
- 风险边界：
  - 是否存在需要交互后才出现的隐藏 surface
  - 是否存在后端不可用、权限不足、校验失败、warning / error banner 等异常态

环境前提：

- 需要能读取宿主项目文件，并能访问目标页面或其等价本地环境
- 若要判断“是否贴近 XYLINK”，必须能看到真实渲染结果；不能只靠代码、CSS、DOM 或静态推断

## Reference Loading Guide

按需读取资料，避免 profile skill 重新变成大手册：

- 缺少参考包、只拿到 demo URL 或只拿到零散截图时，读取 [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)
- 发现编辑链路、step、二级路由、二次确认弹窗容易漏检时，读取 [references/deep-surface-discovery-checklist.md](references/deep-surface-discovery-checklist.md)
- 发现内容显示不全、help/error 文案挤压、布局节奏失衡时，读取 [references/content-layout-checklist.md](references/content-layout-checklist.md)
- 需要按 `writing-skills` 口径做 Baseline / With Skill 压测时，读取 [references/pressure-scenarios.md](references/pressure-scenarios.md)
- 需要给人工发起补漏 review、验收 review 或证据不足 review 时，读取 [references/review-prompt-templates.md](references/review-prompt-templates.md)
- 需要统一登记复合场景、隐藏 surface 和异常态覆盖范围时，运行 [scripts/build_surface_manifest.py](scripts/build_surface_manifest.py)

## Workflow Paths

### Path 1: 构建 XYLINK 参考包

1. 先读取 [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)。
2. 把 XYLINK UIKit demo 视为视觉样例库，而不是实现来源。
   - 只抽视觉契约
   - 不复制源码、构建产物、CSS / JS / 字体 / 图标
3. 判断参考是否足够。
   - 只有 URL、没有真实渲染结果时，先补组件截图
   - 只有原子组件截图、缺少复合业务页时，先补筛选条、配置表单、编辑弹窗、空态下拉等场景
   - 缺少编辑后页面、step、二级路由、二次确认弹窗的真实渲染结果时，不进入正式实施
   - 缺少长文案、help/error 文案、多行说明和窄容器内容承载样例时，不进入正式实施
   - 缺少隐藏 surface 或异常态截图时，不进入正式验收
4. 输出“参考包已就绪”或“仍缺哪些组件 / 状态 / 场景”。

### Path 2: 实施 XYLINK 风格迁移

1. 先记录宿主项目最小上下文。
   - 目标页面 / 路由
   - 样式入口、共享组件目录、共享布局目录
   - 关键交互触发器与异常态复现条件
   - 如怀疑存在漏检深层链路，读取 [references/deep-surface-discovery-checklist.md](references/deep-surface-discovery-checklist.md)
   - 如怀疑存在内容展示或排版问题，读取 [references/content-layout-checklist.md](references/content-layout-checklist.md)
2. 盘点 legacy 组件与真实业务场景。
   - 不停留在原子组件层
   - 至少覆盖筛选工具栏、配置表单、编辑弹窗 / 抽屉、帮助文案区、横向选项组 / segmented rail
   - 还要覆盖编辑后打开的详情页、step 页面、二次确认弹窗和二级路由
3. 抽取 XYLINK 视觉契约。
   - 覆盖 default / hover / active / focus / disabled / selected / error 等关键状态
   - 覆盖长文案、placeholder-only trigger、空值、禁用态、异常反馈
4. 应用内容容量规则。
   - 页面内容布局是强制验收项，不是“风格差不多后顺手看一下”
   - 对有文字承载职责的组件，先记录内容容量，再做视觉收敛
   - 对 `dropdown / select / cascader / autocomplete / segmented rail`，先保证 `trigger` 可识别和已选内容可读，再调整密度和边框
   - 当 XYLINK 参考更窄但宿主真实内容更长时，优先使用更稳妥的 `min-width`、`panel` 扩容、局部换行或减少次级信息，而不是直接截断或无限拉长
   - 若使用 `ellipsis`，必须保证关键信息前缀可读，并提供不依赖 hover 的补充查看路径
   - 对页面级布局至少补一轮 `content / layout cases`，覆盖 label/control/help text、error text、多行说明、footer 按钮组、空态/placeholder、窄容器和长文案
5. 固定实施顺序。
   1. theme / token alias
   2. shared component overrides
   3. shared layout density / spacing
   4. page-level patches
   - 相同 XYLINK 风格修复若跨 2 个以上页面重复出现，默认必须下沉到共享层
6. 严格守住实现边界。
   - 允许 className、data-attribute、纯展示层 wrapper、仅影响外观的 prop
   - 不允许 API、数据流、权限、路由、事件行为改动
   - 不允许为了“更像 XYLINK”而替换组件或引入新的 UI 运行时依赖
7. 对隐藏 surface 做 interaction sweep。
   - 至少覆盖 click、tab 切换、展开 / 收起、dropdown item、row action、hover、focus、selection、route jump
   - 如果某个入口会继续打开二级页面、二级弹窗或确认弹窗，要把整条链路继续展开
   - 不得只看默认页和示例入口
8. 对异常态做 exception sweep。
   - 至少覆盖后端不可用、登录失败 / 校验失败、权限不足、warning / error banner 等可复现项
   - 只允许用 mock、测试环境开关、浏览器级 request blocking 等低风险手段复现
9. 出现以下任一情况时，必须运行 [scripts/build_surface_manifest.py](scripts/build_surface_manifest.py) 固化覆盖范围：
   - 目标页面多于 1 个
   - 存在编辑后打开的详情页、二级路由、step 页面或二次确认弹窗
   - 存在明显内容承载风险，如长文案、help/error text、多行说明、窄容器
   - 存在异常态
   - 需要多人协作或批量回看
10. 必须在 manifest 中补齐 `Content/Layout Cases`、`Breakpoint Coverage`、`Unverified Items` 和 `Exit Checklist`；未补齐前不得声称完成。
11. 在声称完成、收敛或通过前，运行 [scripts/lint_surface_manifest.py](scripts/lint_surface_manifest.py) 校验 manifest 已去除 `TODO` 占位、Exit Checklist 已勾选、证据字段已填写；lint 未通过时，不得宣称完成。
12. 执行最小相关验证，并至少回看 2-3 个真实业务页面。
13. 默认在路径 2 结束；只有用户明确要求验收、审查当前改动或提供了当前 diff 时，才进入路径 3。

### Path 3: XYLINK 口径验收

1. 仅在用户明确要求验收、审查当前改动，或已经提供当前 diff 时进入本路径。
   - 不要为路径 3 主动扩展到 `git log`、历史提交或分支对比
2. 先确认核心组件是否明显向 XYLINK 规范收敛。
   - Button、Input、Table、Form、Modal、Navigation、Tag、Pagination
3. 再确认内容承载平衡。
   - `trigger`、`dropdown`、`segmented`、`tab`、`table cell` 中的关键主文案没有因为控件过窄而长期不可读
   - 组件没有为了显示全文被异常拉长，挤压同排关键控件或撑坏容器节奏
   - `dropdown / popover / panel` 可以比 `trigger` 宽，但仍受页面和视口约束，不会撑爆布局
   - 若存在截断，已证明这是结构预算下的合理取舍，且全量内容有稳定查看路径
4. 再确认真实业务场景。
   - 配置表单和弹窗中的 label / control / help text / footer 按钮组已收敛
   - 编辑后打开的详情页、step 页面、二次确认弹窗已回看
   - 横向选项组中的文案、chip、按钮和选中态没有截断、挤压和异常留白
   - placeholder-only trigger、空态下拉和只读 / 禁用态没有异常收窄
5. 再确认隐藏 surface 和异常态。
   - 交互后才出现的 modal / drawer / popover / tab panel 没有被漏检
   - 特殊异常态下的 banner、提示卡片和反馈文案已做样式回看
   - manifest 中的 `Unverified Items` 与最终汇报一致，没有隐去风险
6. 再确认边界和 copy risk。
   - 没有替换原组件
   - 没有复制 XYLINK 站点实现
   - 没有任何非 UI 改动
7. 若用户要求检查代码边界，只查看当前相关 diff，确认没有复制 XYLINK 站点实现、没有任何非 UI 改动。
8. 报告 remaining visual gaps，并说明是参考缺失还是 legacy 能力限制。

## Reusable Resources

### scripts/

- [scripts/build_surface_manifest.py](scripts/build_surface_manifest.py)
  生成统一的 Markdown 覆盖清单，记录复合场景、交互后 surface、深层编辑链路、内容布局案例、异常态和非 UI 边界证据，适合 XYLINK 风格迁移的批量回看和多人协作。

### references/

- [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)
  读取 XYLINK 参考源、禁止复制规则、抓图优先级和验收口径。
- [references/deep-surface-discovery-checklist.md](references/deep-surface-discovery-checklist.md)
  排查编辑后页面、step、二级路由、二次确认弹窗等深层 surface 是否被漏检。
- [references/content-layout-checklist.md](references/content-layout-checklist.md)
  排查内容展示不全、长文案、help/error 文案、多行说明和布局节奏问题。
- [references/pressure-scenarios.md](references/pressure-scenarios.md)
  提供 `Baseline -> With Skill` 压测场景，用于验证 agent 是否真的要求 manifest、标记 unverified、继续展开深层链路。
- [references/review-prompt-templates.md](references/review-prompt-templates.md)
  提供可直接复制的人工补漏 review、验收 review 和证据不足 review prompt。
- [scripts/lint_surface_manifest.py](scripts/lint_surface_manifest.py)
  在宣称完成前校验 manifest 是否仍含 `TODO`、是否遗漏 Exit Checklist 勾选或关键证据。

## Verification Matrix

| Path | Check | Evidence |
| --- | --- | --- |
| 路径 1 | XYLINK 参考包覆盖核心组件、关键状态、复合场景、隐藏 surface、深层编辑链路、异常态和内容承载样例 | 截图清单、缺失项说明、必要时附 manifest |
| 路径 2 | 只改了 presentation layer，且关键页面、隐藏 surface、深层页面和异常态已被真实回看 | 受影响文件摘要、最小验证结果、前后截图或观察记录、已填写的 manifest（含 content/layout、breakpoint、unverified），必要时附命令摘要 |
| 路径 3 | 结果向 XYLINK 规范收敛且未越界，或明确标记未验证项 | 验收结论、真实观察证据、共享层 / 页面补丁归因说明、剩余差异、manifest 未验证项摘要，必要时附当前 diff 摘要 |

## Failure and Escalation

以下情况不要继续实现：

- 只有 XYLINK demo URL，没有可核对截图或真实渲染结果
- 宿主项目运行方式、目标页面或样式入口不清
- 无法真实查看宿主页面、隐藏 surface 或异常态效果
- 相同 XYLINK 风格修复已在多个页面重复出现，却仍散落在页面补丁中且无法说明原因
- 为了更像 XYLINK，开始尝试替换组件或引入新 UI 运行时依赖
- 为复现异常态准备扰动共享环境、关闭公共服务、修改公共配置或污染真实数据
- 需要访问受限环境或执行高风险命令但尚未批准

## Reporting

### XYLINK legacy component skinning summary
- reference assets used:
- host project scope:
- legacy components kept unchanged:
- composite surfaces checked:
- interactive surfaces checked:
- deep edit/detail flows checked:
- exception surfaces checked:
- content/layout cases checked:
- shared theme / token changes:
- shared component skin overrides:
- page-level visual patches:
- verification:
- unverified items:
- copied XYLINK code/assets: none
- component replacements: none
- non-UI changes: none
- remaining visual gaps:
- assumptions:
