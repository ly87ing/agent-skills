---
name: xylink-legacy-component-skinning
description: "当参考视觉规范明确来自 XYLINK UIKit demo https://precdn.xylink.com/public/uikit/demo/index.html，且要求保留 legacy 前端组件和行为、只做 presentation layer skinning 时使用。先读取 sibling skill ../legacy-component-skinning/SKILL.md 作为通用 workflow，再应用 XYLINK 专属参考抓取、验收口径与禁止复制实现的约束。"
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
   - 优先共享 token / shared overrides
   - 先抓参考包，再做实现，再做组件矩阵验收

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
4. 报告 remaining visual gaps，并说明是参考缺失还是 legacy 能力限制。

## Reusable Resources

### scripts/

当前未内置脚本；如果 XYLINK 参考包抓取和验收成为高频工作，优先补这类 helper：

- `capture_xylink_reference_manifest.*`
  汇总已抓取的 XYLINK 组件截图和状态覆盖。
- `check_xylink_copy_risk.*`
  辅助扫描是否误引入 XYLINK 参考资源、选择器或构建产物痕迹。

### references/

- [../legacy-component-skinning/SKILL.md](../legacy-component-skinning/SKILL.md)
  通用 workflow。
- [references/xylink-uikit-profile.md](references/xylink-uikit-profile.md)
  XYLINK 参考源和禁止复制的附加规则。

## Verification Matrix

| Path | Check | Evidence |
| --- | --- | --- |
| 路径 1 | core workflow 已载入或 fallback 规则已明确 | 读取文件路径或执行说明 |
| 路径 2 | XYLINK 参考包覆盖核心组件、关键状态和真实复合场景 | 截图清单、组件契约、映射表 |
| 路径 3 | 结果向 XYLINK 规范收敛且未越界 | 验收清单、最小验证结果、剩余差异 |

## Failure and Escalation

以下情况不要继续实现：

- 只有 XYLINK demo URL，没有可核对截图或真实渲染结果
- 宿主项目运行方式、目标页面或样式入口不清
- 为了更像 XYLINK，开始尝试替换组件或引入新 UI 运行时依赖
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
