# 参考抓取要求

## 为什么需要这个文件
只有在能看到真实渲染结果时，才能稳定抽取组件视觉契约。仅凭 URL、源码壳页面或零散片段，不足以支撑 skinning 实施。

## 验证原则
- 真实查看效果是硬要求，工具不是硬要求。
- 可以用浏览器直接操作、DevTools、Playwright、录屏回传或人工截图，只要能够观察真实渲染结果。
- 仅看代码、CSS、DOM、静态截图命名或人工推断，不算完成视觉验证。
- 如果拿不到真实渲染结果，只能整理上下文和风险，不能下“已对齐 / 已通过”的确定性结论。

## 最低参考包
至少具备以下其中一种：
- 真实浏览器中的组件截图
- 设计稿中的组件截图
- 内部组件规范或已经整理好的视觉契约文档

## 必须覆盖的内容
至少要有：
- 核心组件默认态
- 核心组件关键状态，如 hover / focus / disabled
- 整页截图，用于判断密度、层级、留白
- 至少 2-3 个真实业务复合场景截图，用于判断表单、弹窗、工具栏和帮助块的布局
- 若页面存在横向选项组、segmented rail 或特性分组，必须抓取其默认态、长文案态、选中态
- 若页面存在交互后才出现的关键界面，必须抓取触发前后成对截图
- 若页面存在系统级错误提示、降级横幅、校验失败反馈，也必须抓取正常态 / 异常态成对截图

## 建议抓取范围

### Button
- primary / secondary / text / danger
- default / hover / active / disabled / loading
- 不同尺寸

### Input / Select / Textarea
- default / focus / disabled / error
- prefix / suffix / clear / placeholder
- 高度、内边距、边框、状态色
- select trigger 在空值、已选值、展开态下的宽度和可见性

### Table
- header
- row hover
- selected row
- checkbox / operation column / pagination
- 行高、分割线、表头层级

### Form
- label
- help text
- error message
- section spacing
- item spacing
- 多种控件混排时的 label 对齐、control 列宽、帮助文案缩进

### Tag / Badge
- 常见语义色
- size
- fill / outline

### Modal / Drawer / Popover
- 标题区
- 内容区
- footer
- 关闭按钮
- mask / shadow / radius
- 提示 banner / 说明卡片 / 表单块之间的间距和对齐

### Navigation
- top nav / side nav / tabs / breadcrumb
- default / hover / active / selected

### Composite business surfaces
- 列表页筛选工具栏
- 配置表单或设置页
- 编辑弹窗或上传/接入弹框
- 日志/审计/监控页面的检索区
- 卡片内横向选项组 / segmented rail / 特性分组
- 任何交互后才出现的 surface，如修改密码、更多菜单、高级配置、tab 切换、hover reveal、row action、route jump
- 异常态 surface，如后端不可用、请求失败、权限不足、校验失败、warning banner

## 抓取原则
- 逐组件抓，不要只抓整页
- 同时保留整页截图，辅助判断层级与密度
- 尽量覆盖状态，而不是只有默认态
- 同一组件不同尺寸放在同一组里
- 统一命名，便于比对
- 额外保留空值、placeholder-only、disabled、长文案、多行说明等极端状态
- 对隐藏 surface 使用成对命名，如 `change-password-before.png` / `change-password-after.png`
- 如果同一页面有多类触发器，命名里带上触发方式或入口名
- 对异常态使用正常/异常成对命名，如 `login-normal.png` / `login-backend-unavailable.png`

## 命名建议
- button-primary-default.png
- button-primary-hover.png
- input-default.png
- input-focus.png
- table-default.png
- modal-default.png

## 当无法拿到所有状态时
如果状态不全：
- 优先抓默认态、focus、hover、disabled
- 缺失状态可从相邻组件或设计规范中谨慎推断
- 推断必须在最终汇报中说明
