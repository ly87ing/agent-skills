# XYLINK UIKit Profile

## Reference Source
- URL: `https://precdn.xylink.com/public/uikit/demo/index.html`
- 用途：把该站点当作组件视觉样例库，而不是可直接搬运的实现来源。

## Hard Rules
- 不复制 XYLINK demo 的源码、构建产物、CSS / JS / 字体 / 图标 / 运行时资源。
- 不把 demo 的 DOM 结构、页面骨架、选择器命名当成迁移目标。
- 不为了更像 XYLINK 而替换宿主项目的 legacy 组件。

## Capture Priority
优先抓取：
- Button、Input、Table、Form、Modal、Navigation、Tag、Pagination
- default / hover / active / focus / disabled / selected 等关键状态
- 整页截图，用于判断密度、层级和留白
- 真实业务页中的配置表单、筛选工具栏、编辑弹窗、空态下拉
- 卡片内横向选项组、特性分组、长文案与选中态徽标
- 各类交互后才出现的二级界面，不限于修改密码、更多菜单、高级配置、tab 切换
- 各类异常态和降级态，如后端不可用、warning banner、登录失败、权限不足

## Acceptance Notes
- 目标是“组件皮肤统一并明显贴近 XYLINK 新规范”，不是“把页面抄成 demo”。
- 若 legacy 组件能力不足，先记录差异，不得以替换组件规避。
- 最终汇报中要明确写出使用了哪些 XYLINK 参考素材，以及哪些状态仍存在差距。
- 不能只证明原子组件变像了；还要证明真实业务复合场景里的对齐、空态和说明文案也已经收敛。
- 若页面存在横向 rail 或特性分组，必须证明长文案、选中态、chip / 按钮组合在真实容器宽度下仍然成立。
- 若关键界面需要交互后才出现，必须证明这些隐藏 surface 已被实际展开并检查，而不是停留在默认初始页；示例入口不是边界，应按页面做系统性扫描。
- 若关键异常态只在特殊条件下出现，也必须证明这些状态已被实际复现并检查，而不是默认视为不重要。
