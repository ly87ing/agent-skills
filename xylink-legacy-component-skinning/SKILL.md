---
name: xylink-legacy-component-skinning
description: 当用户要让 legacy UI 向 XYLINK UIKit demo 或其截图样例收敛，但又不能替换现有组件、不能改 API / 数据流 / 业务逻辑时使用。适用于用户提供 XYLINK demo URL、截图、页面路径、差异截图、交互入口、异常态复现条件，并要求处理默认页、隐藏 surface、异常态或做 XYLINK 口径验收的场景。
---

# XYLINK Legacy Component Skinning

## Outcome

把 XYLINK UIKit demo 当作视觉样例库，而不是实现来源，在不替换 legacy 组件的前提下完成可核对的 skinning：

- 明确使用了哪些 XYLINK 参考截图和关键状态
- 明确哪些共享层覆盖和页面补丁被实现
- 明确哪些复合业务场景、隐藏 surface 和异常态已被实际回看
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
| “默认页像了，但点开后的弹窗/高级区还是旧皮肤” | Engineering / QA | 可运行页面 + 交互入口 | 路径 2 + 路径 3 |
| “异常 banner、登录失败提示、后端不可用提示和 XYLINK 不一致” | Engineering / QA | 可运行页面 + 异常态复现条件 | 路径 2 + 路径 3 |
| “检查这次改动有没有照搬 XYLINK 实现” | Engineering / QA | diff + XYLINK 参考截图 | 路径 3 |

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
   - 缺少隐藏 surface 或异常态截图时，不进入正式验收
4. 输出“参考包已就绪”或“仍缺哪些组件 / 状态 / 场景”。

### Path 2: 实施 XYLINK 风格迁移

1. 先记录宿主项目最小上下文。
   - 目标页面 / 路由
   - 样式入口、共享组件目录、共享布局目录
   - 关键交互触发器与异常态复现条件
2. 盘点 legacy 组件与真实业务场景。
   - 不停留在原子组件层
   - 至少覆盖筛选工具栏、配置表单、编辑弹窗 / 抽屉、帮助文案区、横向选项组 / segmented rail
3. 抽取 XYLINK 视觉契约。
   - 覆盖 default / hover / active / focus / disabled / selected / error 等关键状态
   - 覆盖长文案、placeholder-only trigger、空值、禁用态、异常反馈
4. 固定实施顺序。
   1. theme / token alias
   2. shared component overrides
   3. shared layout density / spacing
   4. page-level patches
   - 相同 XYLINK 风格修复若跨 2 个以上页面重复出现，默认必须下沉到共享层
5. 严格守住实现边界。
   - 允许 className、data-attribute、纯展示层 wrapper、仅影响外观的 prop
   - 不允许 API、数据流、权限、路由、事件行为改动
   - 不允许为了“更像 XYLINK”而替换组件或引入新的 UI 运行时依赖
6. 对隐藏 surface 做 interaction sweep。
   - 至少覆盖 click、tab 切换、展开 / 收起、dropdown item、row action、hover、focus、selection、route jump
   - 不得只看默认页和示例入口
7. 对异常态做 exception sweep。
   - 至少覆盖后端不可用、登录失败 / 校验失败、权限不足、warning / error banner 等可复现项
   - 只允许用 mock、测试环境开关、浏览器级 request blocking 等低风险手段复现
8. 如果页面较多、触发器较多或需要多人协作，运行 [scripts/build_surface_manifest.py](scripts/build_surface_manifest.py) 固化覆盖范围。
9. 执行最小相关验证，并至少回看 2-3 个真实业务页面。

### Path 3: XYLINK 口径验收

1. 先确认核心组件是否明显向 XYLINK 规范收敛。
   - Button、Input、Table、Form、Modal、Navigation、Tag、Pagination
2. 再确认真实业务场景。
   - 配置表单和弹窗中的 label / control / help text / footer 按钮组已收敛
   - 横向选项组中的文案、chip、按钮和选中态没有截断、挤压和异常留白
   - placeholder-only trigger、空态下拉和只读 / 禁用态没有异常收窄
3. 再确认隐藏 surface 和异常态。
   - 交互后才出现的 modal / drawer / popover / tab panel 没有被漏检
   - 特殊异常态下的 banner、提示卡片和反馈文案已做样式回看
4. 再确认边界和 copy risk。
   - 没有替换原组件
   - 没有复制 XYLINK 站点实现
   - 没有任何非 UI 改动
5. 报告 remaining visual gaps，并说明是参考缺失还是 legacy 能力限制。

## Reusable Resources

### scripts/

- [scripts/build_surface_manifest.py](scripts/build_surface_manifest.py)
  生成统一的 Markdown 覆盖清单，记录复合场景、交互后 surface、异常态和非 UI 边界证据，适合 XYLINK 风格迁移的批量回看和多人协作。

### references/

- [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)
  读取 XYLINK 参考源、禁止复制规则、抓图优先级和验收口径。

## Verification Matrix

| Path | Check | Evidence |
| --- | --- | --- |
| 路径 1 | XYLINK 参考包覆盖核心组件、关键状态、复合场景、隐藏 surface 和异常态 | 截图清单、缺失项说明、必要时附 manifest |
| 路径 2 | 只改了 presentation layer，且关键页面、隐藏 surface 和异常态已被真实回看 | 受影响文件摘要、最小验证结果、前后截图或观察记录、必要时附 manifest |
| 路径 3 | 结果向 XYLINK 规范收敛且未越界 | 验收结论、真实观察证据、共享层 / 页面补丁归因说明、剩余差异 |

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
- exception surfaces checked:
- shared theme / token changes:
- shared component skin overrides:
- page-level visual patches:
- verification:
- copied XYLINK code/assets: none
- component replacements: none
- non-UI changes: none
- remaining visual gaps:
- assumptions:
