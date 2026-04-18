# 深层 Surface 发现清单

> XYLINK 默认页贴近只是第一层。编辑链路、step、二级页面、二次确认弹窗常常还停留在旧皮肤。

## 什么时候必须读这份清单

- 用户明确说“编辑后打开的界面没看”
- 页面存在 `编辑 / 详情 / 配置 / 下一步 / 高级 / 更多` 等链路
- 表格行操作、卡片操作、tab 切换、route jump 后会出现新页面或新 panel
- 已经发现一层弹窗，但不确定有没有二次确认、二级弹窗、step 页面

## 发现原则

- 不按按钮文案碰运气，要按“会改变可见 UI 的触发器”系统枚举
- 每发现一个新 surface，都要继续判断它会不会再打开下一层 surface
- 一条链路要走到“没有新 surface”或“明确标记未验证”为止

## 必扫入口类型

- `click`: button、link、icon button、card action、table row action
- `selection`: tab、segmented、radio、menu item、filter chip
- `disclosure`: accordion、collapse、更多、高级、查看详情
- `overlay`: dropdown、popover、modal、drawer、context menu
- `route`: 二级页面、嵌套路由、详情页、wizard step、侧栏切页
- `post-submit`: 保存后出现的确认弹窗、校验态、error panel、success panel

## 每个深层 Surface 至少记录

- 入口名和触发类型
- 所属链路，例如 `列表页 -> 编辑 drawer -> 删除确认弹窗`
- surface 类型，例如 `route / tab panel / drawer / modal / inline expand`
- 是否已保留触发前 / 触发后证据
- 如果没法继续回看，为什么，以及下一步怎么补

## 失败信号

- 只检查默认页就声称“已向 XYLINK 收敛”
- 只打开第一层 drawer，没有继续看二次确认或 step2
- 明知存在深层页面，却没有把它们写进 manifest 或最终汇报
