---
name: legacy-component-skinning
description: "当需要在不替换 legacy 前端组件、不改 API / 数据流 / 业务逻辑的前提下，处理参考视觉迁移、隐藏交互界面样式问题、异常态或降级态样式问题，以及换肤验收时使用。适用于用户提供参考站点、设计稿截图、组件规范文档或视觉契约包，并指出默认页、交互后弹窗/抽屉/二级面板、异常 banner / 表单报错 / 后端不可用提示等需要统一视觉的问题。"
---

# Legacy Component Skinning

## Outcome

在不替换既有组件库和组件实现的前提下，完成 legacy UI 的展示层换肤，并给出可核对的证据：

- 参考侧素材是否充分
- 旧组件到参考视觉契约的映射是否清晰
- 改动是否严格停留在 presentation layer
- 核心组件在多页面、多状态、多断点下是否进入同一视觉体系
- 真实业务复合场景中的布局、对齐、空态和帮助信息是否也已收敛
- 横向选项组、分组 rail、带徽标的 feature card 是否没有截断、挤压和异常留白
- 通过点击、切换、展开后才出现的隐藏 surface 是否也已被检查
- 异常态、降级态、故障提示和罕见反馈 surface 是否也已被检查
- 仍存在的视觉差异与原因

## Roles and Jobs

- Product / Design:
  - 判断某批 legacy 页面是否适合做视觉对齐
  - 评估参考规范覆盖度、迁移范围和剩余差异
- Engineering:
  - 在不换组件的前提下做共享 token、共享组件覆盖和页面补丁
  - 审查换肤方案是否越过了非 UI 边界
- QA:
  - 按组件矩阵和断点校验迁移结果
  - 确认同类组件在多页面下表现一致

## Trigger Matrix

将常见请求和输入映射到对应路径。

| Trigger | Role | Required context | Path |
| --- | --- | --- | --- |
| “保留旧组件，只改样式，让页面贴近这套新规范” | Engineering | 宿主项目路径 + 参考源 | 路径 2 |
| “帮我盘点老组件和可改的样式入口” | Engineering | 目标页面、组件目录、样式入口 | 路径 2 |
| “只有设计稿/截图，先整理参考包再改” | Product / Engineering | 截图、设计稿、参考站点 URL | 路径 1 |
| “检查这次换肤是否改到了非 UI 逻辑” | Engineering / QA | diff、目标页面、组件映射 | 路径 3 |
| “验收 legacy skinning 是否统一” | QA | 可运行页面、参考包、断点要求 | 路径 3 |
| “页面能跑，但弹窗、配置表单、空态下拉还是很乱” | Engineering / QA | 真实页面截图或可运行页面 | 路径 2 + 路径 3 |
| “有些问题藏在点开之后才出现的界面里” | Engineering / QA | 可运行页面 + 可交互入口 | 路径 2 + 路径 3 |
| “特殊报错、后端不可用、异常提示样式也要一起检查” | Engineering / QA | 可运行页面 + 异常态复现条件 | 路径 2 + 路径 3 |

## Context Sources

开始执行前先收齐最小上下文：

- 宿主项目：
  - 启动命令、构建命令、本地访问地址
  - 目标页面 / 路由
  - 样式入口、theme/token 文件、共享组件目录
  - 所有会改变可见 UI 的关键交互触发器：button、link、tab、segmented control、dropdown item、row action、accordion、hover/focus reveal、wizard step、route jump 等
  - 可复现的异常态入口：后端断连、请求失败、权限不足、表单校验失败、空数据、超时、只读锁定、功能未开启
- 参考侧：
  - 可访问的参考站点
  - 设计稿截图或人工整理的视觉契约
  - 至少覆盖核心组件默认态和关键状态的参考包
- 至少覆盖 2-3 个真实业务复合场景，如筛选工具栏、配置表单、编辑弹窗
- 如果页面存在横向选项组、特性分组或 segmented rail，必须纳入参考包
- 如果页面存在异常横幅、错误页、降级提示、warning banner，也必须纳入参考包
- 验证环境：
  - 真实查看效果的手段，如浏览器直接操作、DevTools、Playwright、录屏回传或人工截图
  - 需要覆盖的断点
  - 目标项目是否有现成测试或 smoke 命令
  - 是否有可用于展开隐藏 surface 的浏览器交互手段，如 DevTools、Playwright 或人工浏览器操作
  - 异常态只允许通过本地、隔离测试环境、浏览器级 request blocking / mock、环境开关、URL 参数、测试账号等可逆低风险手段触发
- 审批与停止条件：
  - 没有可核对参考包时，不进入正式样式改造
  - 宿主项目跑不起来或范围不清时，不猜样式、不盲改
  - 无法真实查看渲染结果、交互结果或异常态结果时，不给出“已统一 / 已通过 / 已验证”的确定性结论
  - 不得为了复现异常态去停共享服务、改公共配置、污染公共数据或破坏真实后端；如果只能用这类手段，先升级并请求批准
  - 需要安装依赖、打开外部页面或执行高风险命令时，先请求批准

环境前提：

- 需要能读取宿主项目文件，并能访问目标页面或其等价本地环境
- 需要一种真实观察渲染结果的方式，例如浏览器、DevTools、Playwright、录屏回传或人工截图

## Reference Loading Guide

按需读取 reference，不把所有细节一次性灌进主流程：

- 参考包不足或只有零散截图 / URL 时，读取 [references/reference-capture-requirements.md](references/reference-capture-requirements.md)
- 正式动手前，先填写 [references/host-project-context-template.md](references/host-project-context-template.md)
- 盘点 legacy 组件与共享覆盖点时，读取 [references/legacy-component-map-template.md](references/legacy-component-map-template.md)
- 抽取视觉契约时，读取 [references/component-visual-contract-template.md](references/component-visual-contract-template.md)
- 发现复合业务页错位时，读取 [references/composite-surface-checklist.md](references/composite-surface-checklist.md)
- 发现隐藏 surface 问题时，读取 [references/interactive-surface-checklist.md](references/interactive-surface-checklist.md)
- 发现异常态或降级态问题时，读取 [references/exception-state-checklist.md](references/exception-state-checklist.md)
- 最终验收时，读取 [references/visual-acceptance-checklist.md](references/visual-acceptance-checklist.md)

## Workflow Paths

### Path 1: 补齐参考包

1. 判断现有参考是否足够支撑实现：
   - 如果只有 URL、HTML 壳页面或零散源码片段，视为不足。
   - 如果只有整页截图但缺少核心组件状态，也视为不足。
   - 如果只有原子组件截图，但缺少真实业务布局中的复合场景，也视为不足。
   - 如果页面存在横向选项组或特性分组，但参考包未覆盖其长文案、选中态和窄容器表现，也视为不足。
   - 如果页面中大量界面需要交互后才出现，但参考包未覆盖这些交互后 surface，也视为不足。
   - 如果系统存在异常横幅、错误提示、后端不可用等特殊状态，但参考包未覆盖这些罕见状态，也视为不足。
2. 按需读取 [references/reference-capture-requirements.md](references/reference-capture-requirements.md)。
3. 抓取或整理最小参考包：
   - 逐组件抓取真实渲染结果
   - 记录尺寸、状态、密度和层级
   - 补充真实业务复合场景截图，覆盖空值、占位态、禁用态、长文案和帮助信息
   - 对隐藏 surface 保留“触发前 / 触发后”成对截图，覆盖所有关键可见状态变化，而不是只挑 1-2 个显眼按钮
   - 对异常态仅使用本地 / 测试环境 / 浏览器级可逆手段复现，并保留“正常态 / 异常态”成对截图，如 mock 成功与 mock 失败、校验前与校验失败后
   - 将推断项和缺失项单独标注
4. 输出“可核对参考包已就绪”或“仍缺哪些组件/状态”。

### Path 2: 实施 skinning 迁移

1. 按需读取以下模板并补齐信息：
   - [references/host-project-context-template.md](references/host-project-context-template.md)
   - [references/legacy-component-map-template.md](references/legacy-component-map-template.md)
   - [references/component-visual-contract-template.md](references/component-visual-contract-template.md)
2. 盘点 legacy 组件：
   - 组件名、来源、页面位置、当前 variant / size / state
   - 样式入口、共享层可改点、局部补丁需求
3. 同步盘点真实业务复合场景，不要停在原子组件层：
   - 搜索/筛选工具栏
   - 列表页顶部操作区
   - 配置表单、日志筛选区、告警配置页
   - 编辑弹窗、抽屉、上传配置弹框
   - 带说明文案、提示块、禁用态、空态下拉的页面
   - 卡片内横向选项组、特性分组、segmented rail
   - 交互后才出现的隐藏 surface，如二级弹窗、drawer、popover、行内展开区、切 tab 后面板、hover/focus 后出现的操作区
   - 异常态 surface，如 error banner、warning banner、empty-error hybrid、后端不可用提示、校验失败提示、超时提示、权限受限提示
   - 对每个场景记录标签宽度、控件列宽、按钮组、帮助文案、空态/占位态、disabled/read-only 状态
   - 对横向选项组额外记录：是否允许换行、最小宽度、文本截断、组内间距、徽标/标签与主文案基线
   - 对隐藏 surface 额外记录：触发入口、触发方式（click / hover / focus / selection / route jump）、可见条件、打开后的布局、关闭后的回退状态
   - 对异常态额外记录：触发条件、是否可重复复现、提示层级（page / card / form / inline）、图标/文案/操作按钮/边框背景的状态关系
4. 抽取参考视觉契约：
   - 只抽效果，不复制参考实现、选择器体系或构建产物
   - 覆盖默认态、hover、active、focus、disabled、selected、error 等关键状态
   - 覆盖 value present / value absent、placeholder、长文案、下拉展开态等业务常见状态
5. 建立语义映射：
   - 按视觉作用和交互语义映射 legacy component -> reference contract
   - 优先共享 token / 主题层，再共享组件覆盖，最后页面补丁
   - 同一类视觉修复如果在 2 个以上页面、弹窗或 surface 中重复出现，默认必须下沉到共享 token、shared override 或共享 layout 层，而不是分别打页面补丁
6. 固定实施顺序：
   1. theme / token alias
   2. shared component overrides
   3. shared layout density / spacing
   4. page-level visual patches
   - `page-level visual patch` 只能处理页面特有的结构差异、容器约束或临时过渡，不得承载通用皮肤规则
7. 仅在无法落地时做最小接线：
   - 允许 className、data-attribute、纯展示层 wrapper、仅影响外观的 prop
   - 不允许 API、数据流、权限、路由、事件行为改动
8. 按需读取以下清单做专项扫描：
   - [references/common-visual-regressions.md](references/common-visual-regressions.md)
   - [references/composite-surface-checklist.md](references/composite-surface-checklist.md)
   - [references/interactive-surface-checklist.md](references/interactive-surface-checklist.md)
   - [references/exception-state-checklist.md](references/exception-state-checklist.md)
9. 如果目标页面较多、触发器较多或需要多人协作，先运行 [scripts/build_surface_manifest.py](scripts/build_surface_manifest.py) 生成统一的覆盖清单，避免漏检和证据漂移。
10. 如果页面包含隐藏 surface，必须先做一次 interaction sweep，再检查：
   - 系统枚举所有会改变可见 UI 的触发器，而不是只看文案最显眼的按钮
   - 至少覆盖 click、tab 切换、展开/收起、dropdown item、row action、hover、focus、selection、route jump
   - 每发现一个新 surface，都要补一次布局与状态检查
   - 不得只根据默认初始页断言“页面样式正常”
11. 如果系统存在罕见异常态，必须补一次 exception sweep：
   - 系统枚举所有会让页面从 happy path 转入 degraded / error / warning / empty-error 的条件
   - 至少覆盖接口失败、后端不可用、表单校验失败、权限不足、功能未开启、空数据异常提示中的可复现项
   - 只允许使用 mock、浏览器 request blocking、测试环境专用开关、隔离数据或其它可逆低风险手段；不得为了看到异常 UI 去停共享服务、改公共地址或破坏真实后端
   - 不得因为“场景少见”就默认忽略其样式质量
12. 所有布局、对齐、状态和收敛判断都必须基于真实渲染后的实际观察，不得仅凭代码、CSS、DOM、截图命名或静态推断判定“已经对齐”。
13. 执行最小相关验证，并至少回看 2-3 个真实业务页面，而不是只看组件 playground。

### Path 3: 评审与验收

1. 对照 [references/visual-acceptance-checklist.md](references/visual-acceptance-checklist.md)。
2. 以组件矩阵而不是单页截图做验收：
   - 同类组件跨页面是否统一
   - 核心状态是否统一
   - 高度、圆角、边框、阴影、密度是否统一
   - 断点下是否正常
3. 再以“复合场景矩阵”做验收：
   - 空值下拉、placeholder-only trigger 是否收窄或难以识别
   - 下拉面板展开后选项、选中态、hover 态是否可见
   - 混合表单中的 label、control、help text、必填星号是否对齐
   - 弹窗中的说明块、表单块、footer 按钮组是否在同一布局节奏
   - 横向选项组中的长文案、选中徽标、分组间距、overflow / wrap 策略是否正确
   - 只读/禁用态是否仍保持正确的宽度、层级和可读性
4. 再以“交互态 surface 矩阵”做验收：
   - 所有关键可见状态变化入口是否已做 interaction sweep
   - 新出现的弹窗 / drawer / popover / 内嵌表单是否存在对齐、截断、留白和层级问题
   - 触发前后样式是否连续，不会一打开就退回旧皮肤
5. 再以“异常态矩阵”做验收：
   - 后端不可用、权限不足、校验失败、空数据异常等罕见状态是否已回看
   - 异常 banner / alert / inline error 的图标、文案、边框、背景、间距和层级是否协调
   - 异常态不会因为只在特殊条件下出现而继续沿用旧皮肤
6. 再复核“验收结论是否来自真实观察”：
   - 至少有真实渲染、真实交互或真实异常反馈的观察证据
   - 不能只依据代码 diff、CSS 变量、DOM 结构或人工推断给出通过结论
   - 若某页或某状态无法真实查看，只能标记为未验证
7. 再复核“可复用内容是否已下沉”：
   - 跨 2 个以上页面重复出现的视觉修复，已优先下沉到 token、shared override 或共享 layout
   - 页面补丁只承载页面特有结构差异，而不是重复皮肤规则
   - 若仍保留多个相似页面补丁，已明确说明为什么无法收敛到共享层
8. 复核实现边界：
   - 原组件是否仍为原组件
   - 是否有任何非 UI 层改动
   - 是否引入了新的 UI 运行时依赖或复制参考资源
9. 报告完成项、剩余差异、假设和风险。

## Reusable Resources

### scripts/

- [scripts/build_surface_manifest.py](scripts/build_surface_manifest.py)
  生成统一的 Markdown 覆盖清单，强制把复合场景、交互后 surface、异常态和非 UI 边界证据放进同一份 manifest，适合多人协作或大页面群回看。输入是页面名、路由、复合场景、交互触发器和异常态定义；输出是可直接补证据的 checklist / table。
  在触发器较多、异常态较多或需要批量回看时优先运行它，而不是手工拼接截图清单。

### references/

- [references/reference-capture-requirements.md](references/reference-capture-requirements.md)
  参考包不足时读取，明确最低抓取范围与命名方式。
- [references/host-project-context-template.md](references/host-project-context-template.md)
  开始改代码前填写，避免在宿主项目中盲改。
- [references/legacy-component-map-template.md](references/legacy-component-map-template.md)
  盘点旧组件与共享层覆盖点。
- [references/component-visual-contract-template.md](references/component-visual-contract-template.md)
  把参考规范抽象为可实现的视觉契约。
- [references/visual-acceptance-checklist.md](references/visual-acceptance-checklist.md)
  用于最终验收。
- [references/common-visual-regressions.md](references/common-visual-regressions.md)
  排查常见工程化视觉陷阱。
- [references/composite-surface-checklist.md](references/composite-surface-checklist.md)
  排查真实业务页里的对齐、空态、弹窗和表单布局问题。
- [references/interactive-surface-checklist.md](references/interactive-surface-checklist.md)
  排查点击后才出现的隐藏页面、二级弹窗和延迟渲染区域。
- [references/exception-state-checklist.md](references/exception-state-checklist.md)
  排查异常态、降级态、报错提示和罕见反馈样式问题。

## Verification Matrix

在声称完成前，至少提供以下证据。

| Path | Check | Evidence |
| --- | --- | --- |
| 路径 1 | 参考包覆盖核心组件、关键状态、真实复合场景、交互后 surface 和异常态 | 截图清单、命名列表、缺失项说明、必要时附 manifest |
| 路径 2 | 只改了 presentation layer，且核心页面与关键弹窗/表单/隐藏 surface / 异常态能运行并被真实回看 | 最小测试结果、页面访问结果、前后截图或观察记录、受影响文件摘要、必要时附 manifest |
| 路径 3 | 组件矩阵、复合场景矩阵、交互态 surface 矩阵、异常态矩阵、共享层收敛与非 UI 边界均通过 | 验收清单、真实观察证据、共享层 / 页面补丁归因说明、剩余差异列表、断点检查说明 |

## Failure and Escalation

遇到以下情况时停止或升级，而不是继续猜：

- 参考规范缺失关键组件或状态：先补参考包
- 宿主项目无法运行、范围不清、样式入口未知：先补上下文
- 无法真实查看渲染结果、交互结果或异常态结果：停止确定性验收，只报告未验证项与阻塞原因
- 相同视觉修复已在多个页面重复出现，却仍散落在页面补丁中且无法说明原因：停止验收，先评估共享层下沉方案
- 旧组件能力不足以 1:1 还原：记录可接受退化，不得以替换组件规避
- 参考资源存在 license / copy 风险：只抽视觉契约，不搬源码、构建产物、CSS / JS / 字体 / 图标
- 为复现异常态必须扰动共享环境、关闭公共服务、修改公共配置或污染真实数据：停止并升级，不得自行操作
- 需要安装依赖、访问受限环境、执行高风险命令：先请求批准

## Reporting

完成后按以下结构汇报：

### Legacy component skinning summary
- reference source:
- host project scope:
- legacy components kept unchanged:
- composite surfaces checked:
- interactive surfaces checked:
- exception surfaces checked:
- shared theme / token changes:
- shared component skin overrides:
- page-level visual patches:
- verification:
- copied reference code/assets: none
- component replacements: none
- non-UI changes: none
- remaining visual gaps:
- assumptions:
