# 交互后出现的隐藏 Surface 检查清单

> 很多 UI 问题不在默认初始页，而在用户点了一次之后才暴露。

## 目标

确保 agent 不只检查“打开页面第一眼看到的内容”，还会主动探索那些需要交互后才显示的界面。

下面列出的入口是常见示例，不是边界。原则是：

- 任何会改变可见 UI 的交互，都可能暴露新的 surface
- 不要把“修改密码 / 更多 / 高级”当成固定清单然后机械点完就停止
- 要按页面结构做 discovery，而不是按按钮文案碰运气

## 入口发现法

对每个目标页面，先枚举所有“可能让新的 UI 出现”的触发器：

- click：按钮、链接、图标按钮、卡片项、列表项、表格行操作
- selection：tab、segmented control、radio group、filter chip、menu item
- disclosure：accordion、collapse、更多、展开、查看详情、advanced section
- overlay：dropdown、popover、tooltip、context menu、modal、drawer
- hover / focus reveal：hover 后出现的操作列、focus 后出现的 suffix action、password eye icon
- route change：切换二级页面、step、wizard、详情页、嵌套路由
- state change：提交后校验失败、请求失败后重试、后端不可用后的降级反馈

任何一个触发器如果会改变：

- 可见内容
- 布局结构
- 控件状态
- 覆盖层类型

就应该被纳入检查范围。

## 常见隐藏 Surface

- 点击“修改密码”后出现的弹窗或内嵌表单
- 点击“更多”后出现的菜单、下拉列表、二级操作面板
- 点击“高级”后展开的参数区、accordion、折叠卡片
- 切换 tab、step、分段控制后才出现的内容区
- 点击“编辑 / 配置 / 新增 / 查看详情”后出现的 drawer、modal、popover
- hover、focus、选中某行后才出现的工具条和操作按钮

## 必做探索

如果页面存在以下入口，至少逐类打开一次：

- `修改密码`
- `更多`
- `高级`
- `编辑`
- `配置`
- `查看详情`
- tab 切换
- accordion / collapse 展开
- 表格行 hover 或选中态操作区

这些只是高频样本，不是穷尽列表。

## 每个隐藏 Surface 都要记录

- 入口是什么
- 属于哪类触发器：click / selection / disclosure / overlay / hover / focus / route
- 触发前页面状态
- 触发后 surface 类型：modal / drawer / popover / inline expand / tab panel
- 打开后是否出现新的表单、提示块、按钮组、空态控件
- 关闭后页面是否恢复正常

## 必查问题

- 打开后的 surface 是否仍是旧皮肤
- modal / drawer 的 header、body、footer 是否协调
- 新出现的表单项是否存在 label / control / help text 对齐问题
- 隐藏 surface 中的 select、date picker、password input 是否被压缩或错位
- 打开后是否出现截断、遮挡、z-index、留白过大或滚动异常

## 最小证据

每个关键隐藏 surface 至少保留：

- 1 张触发前截图
- 1 张触发后截图
- 1 条触发入口说明

如果页面有多个入口共享同一 surface，也要说明“哪些入口已归并”，不要默认它们等价。

必须通过真实运行后的界面确认这些隐藏 surface；工具不限，可以是浏览器直接操作、DevTools、Playwright 或人工截图回传。仅看代码、DOM 或静态推断，不算完成检查。
