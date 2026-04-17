---
name: xylink-legacy-component-skinning
description: "当参考视觉规范明确来自 XYLINK UIKit demo，且需要在不替换 legacy 前端组件、不改 API / 数据流 / 业务逻辑的前提下，处理 XYLINK 风格迁移、交互后隐藏界面样式问题、异常态或降级态样式问题，以及换肤验收时使用。适用于用户给出 XYLINK demo URL、截图，或指出弹窗/配置页/异常提示等界面与 XYLINK 规范不一致的场景。"
---

# XYLINK Legacy Component Skinning

## Outcome

在复用通用 `legacy-component-skinning` workflow 的前提下，把 XYLINK UIKit demo 作为参考视觉样例库，完成针对 XYLINK 规范的 legacy UI skinning，并明确：

- 哪些参考截图或组件状态被使用
- 哪些共享层覆盖和页面补丁被实现
- 哪些真实业务复合场景已回看
- 横向选项组、特性分组和分段 rail 是否也已收敛
- 点击后才出现的隐藏 surface 是否已展开检查
- 所有关键可见状态变化入口是否都已做 interaction sweep
- 特殊异常态、降级态和罕见提示样式是否也已展开检查
- 哪些差异来自 legacy 组件能力限制
- 是否严格避免复制 XYLINK 站点实现

## Roles and Jobs

- Engineering:
  - 让 legacy 组件视觉贴近 XYLINK UIKit，同时保留原组件与行为
  - 审查实现是否错误复制了 XYLINK 页面实现或资源
- QA / Design:
  - 使用 XYLINK 参考图和 demo 实际渲染结果做对照验收
  - 标记与 XYLINK 新规范仍未收敛的组件状态

## Trigger Matrix

| Trigger | Role | Required context | Path |
| --- | --- | --- | --- |
| “按 XYLINK UIKit demo 给旧页面换肤” | Engineering | 宿主项目 + XYLINK 参考源 | 路径 2 |
| “不要换组件，只把视觉往 XYLINK 靠” | Engineering | 目标页面 + XYLINK 参考图 | 路径 2 |
| “默认页像了，但点开后的弹窗/高级区还是旧皮肤” | Engineering / QA | 可运行页面 + 交互入口 | 路径 2 + 路径 3 |
| “异常 banner、登录失败提示、后端不可用提示和 XYLINK 不一致” | Engineering / QA | 可运行页面 + 异常态复现条件 | 路径 2 + 路径 3 |
| “检查这次改动有没有照搬 XYLINK 实现” | Engineering / QA | diff + 参考截图 | 路径 3 |

## Context Sources

- 通用 workflow：
  - 首先读取 [../legacy-component-skinning/SKILL.md](../legacy-component-skinning/SKILL.md)
  - 按需读取 sibling references
- XYLINK profile：
  - [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)
  - XYLINK UIKit demo URL
  - 从真实浏览器抓取的组件截图
- 宿主项目：
  - 样式入口、共享组件目录、目标页面 / 路由、本地运行方式

## Workflow Paths

### Path 1: 载入通用 workflow

1. 优先读取 [../legacy-component-skinning/SKILL.md](../legacy-component-skinning/SKILL.md)。
2. 复用通用 skill 中的：
   - 宿主项目上下文模板
   - legacy 组件映射模板
   - 组件视觉契约模板
   - 通用验收清单
3. 如果 sibling skill 不可用，至少遵守：
   - 保留原组件和原行为
   - 只做 presentation layer 改动
   - 先抓参考包，再做实现，再做验收
   - 参考包必须覆盖核心组件、真实复合场景、交互后 surface、异常态 / 降级态
   - 优先共享 token / shared overrides，其次 shared layout density，最后 page-level patches
   - 相同 XYLINK 风格修复若在 2 个以上页面或弹窗中重复出现，默认必须下沉到共享层，而不是散落多个页面补丁
   - 主动做 interaction sweep 和 exception sweep，不得只看默认页和 happy path
   - 异常态只允许通过 mock、测试环境专用开关、浏览器级拦截等低风险手段复现，禁止扰动共享环境
   - 验收必须同时覆盖组件矩阵、复合场景矩阵、交互态矩阵、异常态矩阵，以及 copy risk / non-UI boundary

### Path 2: 构建 XYLINK 参考包并实施

1. 按需读取 [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)。
2. 把 XYLINK UIKit demo 视为“视觉样例库”，而不是实现来源：
   - 只能抽视觉契约
   - 不能复制源码、构建产物、CSS / JS / 字体 / 图标
3. 如果当前只有 URL、拿不到真实渲染结果：
   - 先抓组件截图
   - 再建立视觉契约和 legacy 组件映射
   - 不要根据 HTML 壳页面或源码片段臆测样式
4. 完成实现时，沿用 core skill 的固定顺序：
   1. theme / token alias
   2. shared component overrides
   3. shared layout density / spacing
   4. page-level patches
   - 若相同 XYLINK 皮肤修复跨 2 个以上页面重复出现，默认必须下沉到共享层；`page-level patch` 只能处理页面特有结构差异
5. 必须额外回看真实业务复合场景，而不只看 UIKit 风格的原子组件：
   - 状态筛选下拉
   - 配置表单
   - 编辑弹窗 / 上传配置弹框
   - 带帮助文案或提示块的设置页面
   - 卡片内横向选项组 / 特性分组 / segmented rail
6. 如果存在交互后才出现的界面，必须主动做 interaction sweep：
   - 不限于修改密码、更多菜单、高级配置、tab 切换
   - 还应覆盖 hover、focus、row action、route jump、二级详情入口等所有会改变可见 UI 的触发器
7. 如果系统存在异常态或降级态，必须补一次 exception sweep：
   - 后端不可用
   - 登录失败 / 校验失败
   - 权限不足
   - warning / error banner
   - 只允许使用 mock、测试环境专用开关、浏览器级 request blocking 等低风险手段复现；不得为了看异常 UI 去停共享服务或改公共配置
8. XYLINK 收敛判断必须基于真实效果回看：
   - 可以用浏览器直接操作、DevTools、Playwright、录屏回传或人工截图
   - 不得只凭源码片段、CSS、DOM 或静态推断就断言“已经像 XYLINK”

### Path 3: XYLINK 口径验收

1. 重点核对以下组件是否明显向 XYLINK 规范收敛：
   - Button、Input、Table、Form、Modal、Navigation、Tag、Pagination
2. 同时确认：
   - 没有替换原组件
   - 没有复制 XYLINK 站点实现
   - 没有任何非 UI 改动
3. 额外确认：
   - 空态下拉和 placeholder-only trigger 不会收窄
   - 配置表单和弹窗中的 label / control / help text / footer 按钮组已收敛
   - 横向选项组中的文案、chip、按钮和选中态没有截断、挤压和异常留白
   - 交互后才出现的弹窗、tab panel、popover 和高级区没有被漏检
   - 不是只验证了少数几个示例入口，而是按页面做过系统性入口扫描
   - 特殊异常态下的 banner、提示卡片和反馈文案也已做样式回看
   - 验收结论来自真实渲染与实际回看，而不是代码或静态推断
   - 可复用的 XYLINK 风格修复已经下沉到共享层，而不是散落在多个页面补丁
4. 报告 remaining visual gaps，并说明是参考缺失还是 legacy 能力限制。

## Reusable Resources

### scripts/

- 如果 sibling core 可用，优先运行 [../legacy-component-skinning/scripts/build_surface_manifest.py](../legacy-component-skinning/scripts/build_surface_manifest.py) 生成统一的复合场景 / 交互态 / 异常态覆盖清单。
- 如果 sibling core 不可用，不要假装存在自动化脚本；按 Path 1 fallback 的结构手工记录同样的 manifest 字段和证据。

### references/

- [../legacy-component-skinning/SKILL.md](../legacy-component-skinning/SKILL.md)
  通用 workflow。
- [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)
  XYLINK 参考源和禁止复制的附加规则。

## Verification Matrix

| Path | Check | Evidence |
| --- | --- | --- |
| 路径 1 | core workflow 已载入或 fallback 规则已明确 | 读取文件路径或执行说明 |
| 路径 2 | XYLINK 参考包覆盖核心组件、关键状态、真实复合场景、交互后 surface 和异常态 | 截图清单、组件契约、映射表、必要时附 manifest |
| 路径 3 | 结果向 XYLINK 规范收敛且未越界，并完成交互态 / 异常态 / copy risk / non-UI boundary / shared-layer convergence 复核 | 验收清单、真实观察证据、共享层 / 页面补丁归因说明、最小验证结果、剩余差异、必要时附 manifest |

## Failure and Escalation

以下情况不要继续实现：

- 只有 XYLINK demo URL，没有可核对截图或真实渲染结果
- 宿主项目运行方式、目标页面或样式入口不清
- 无法真实查看宿主页面、交互后 surface 或异常态效果
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
