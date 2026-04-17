# 常见工程化视觉缺陷

## 1. 单行 flex 工具栏未垂直居中
- 症状：搜索栏、按钮区、卡片头部、弹窗 footer 里的元素上下错位。
- 根因：`display: flex` 默认不会自动解决不同高度元素的视觉对齐。
- 处理：对单行 toolbar、header、footer、分页区优先补 `align-items: center`；多行内容再按需保留 `flex-start`。

## 2. 短文案在 flex 容器内被异常折行
- 症状：标签、冒号、短提示语被压成两行。
- 根因：flex 子元素默认可被压缩，短文本宽度不足时会换行。
- 处理：给承载短文案的元素补 `white-space: nowrap`、`flex-shrink: 0`，或调整父容器宽度策略。

## 3. 表格或 tab 内容区滚动被错误捕获
- 症状：滚轮移到表格或 tab 内容区后页面不再继续滚动，或内容只能滚动一小段。
- 根因：局部容器错误设置了 `overflow`，或 flex 链缺少 `min-height: 0`。
- 处理：限定选择器后修正 overflow；逐个 tab 检查从 tabpane 到根节点的 flex 收缩链。

## 4. `inline-flex` / `inline-block` 让表单控件变窄
- 症状：input、select、搜索框没有撑满容器，宽度被内容收缩。
- 根因：inline-level 盒模型默认是 shrink-to-fit。
- 处理：给控件本身或直接父级补 `width: 100%`；必要时补 `min-width: 0`。

## 5. JS 驱动高度动画与 `display: flex` 冲突
- 症状：Collapse / Accordion 展开后内容被截断或高度跳动。
- 根因：组件依赖 `scrollHeight` 计算动画高度，flex 布局会让测量失真。
- 处理：避免把动画根节点或其直接包裹设为 `display: flex`；必要时加 block wrapper。

## 6. orphan 样式与全局覆盖打架
- 症状：全局 token 已更新，但部分页面仍保留旧色、旧间距、异常 z-index。
- 根因：历史页面残留硬编码颜色、局部 hack、magic number 间距。
- 处理：优先清理全局 orphan 样式，用 token / CSS variable 收口；确实无法立刻清理时做限定范围兜底。

## 7. 空值下拉 / placeholder-only trigger 被收窄
- 症状：下拉框在没有选中值时，触发器宽度明显变窄；展开后当前筛选项难以识别。
- 根因：触发器宽度跟随内容 shrink，而不是服从表单列宽或最小宽度；placeholder 样式与真实 value 样式未统一。
- 处理：为 select trigger 建立稳定的 `min-width` / `width` 规则；同时检查 placeholder、selected value、suffix icon 的占位关系。

## 8. 下拉面板展开后选项可见性差
- 症状：点击后虽然出现菜单，但文字、选中态或 hover 态不明显，看起来像“没有内容”。
- 根因：菜单面板宽度、背景、文本颜色、选中态样式没有跟随新皮肤一起调整。
- 处理：检查 dropdown / popover panel 的宽度、前景色、背景色、选中态、hover 态和滚动容器，不要只改 trigger 本体。

## 9. 混合表单的 label / control / help text 不在同一基线
- 症状：表单页中 input、textarea、switch、select、必填星号、帮助文案上下左右不齐。
- 根因：不同控件行高、外边距、label 宽度、help text 缩进规则没有统一。
- 处理：先建立表单行级规则，再调单个控件；统一 label 宽度、control 列宽、help text 缩进、错误文案位置。

## 10. 弹窗中的说明块、表单块、footer 按钮组节奏断裂
- 症状：弹窗顶部提示卡片和表单区域不对齐，底部按钮组像另一个系统。
- 根因：modal body 内多个子区块使用了不同的 padding、border radius、background 和 footer 对齐规则。
- 处理：把 modal 视为复合场景单独验收，统一 header、banner、content、footer 四个层级的间距和对齐。

## 11. 说明文案和提示块换行后缩进失衡
- 症状：多行提示文案第二行开始偏移异常，或与输入组、label 不在同一列。
- 根因：帮助文案继承了错误的 line-height、margin-left 或容器宽度。
- 处理：检查多行换行、长文案、带图标说明块的缩进规则，确保其和所属控件列一致。

## 12. disabled / read-only 控件层级正确但宽度失稳
- 症状：禁用态控件颜色看似正确，但宽度、对齐、placeholder 表现与正常态不一致。
- 根因：禁用态样式单独覆盖了 padding、width、border 或 value 容器样式。
- 处理：把 disabled / read-only 当成独立状态矩阵检查，不要只验证文字颜色。

## 13. 横向选项组错误使用 `space-between` 导致巨大空白
- 症状：同一组里的标题、徽标、按钮之间被拉得很开，视觉上像断裂成几段。
- 根因：父容器使用 `justify-content: space-between` 或固定列宽，但子项内容长度不均。
- 处理：优先建立明确的组内 gap、对齐点和最小宽度，不要用 `space-between` 硬撑整行。

## 14. 横向 rail 使用 `nowrap` 或固定宽度导致文本裁切
- 症状：分组名、特性名、部署项文字被截断，尾部消失或被相邻元素覆盖。
- 根因：子项被设置为不可换行且缺少合理的 `min-width` / `max-width` / `overflow` 策略。
- 处理：根据场景明确选择 wrap、ellipsis 或局部滚动；不要默认 `nowrap` + 固定宽度。

## 15. 徽标 / chip / 次按钮与主文案基线错位
- 症状：蓝色小按钮、状态 chip、标签与相邻文本上下不齐，看起来像浮起来或沉下去。
- 根因：行高、高度、padding 或 `align-items` 在文本和徽标类元素之间不一致。
- 处理：对 rail 内的文本、chip、icon、button 建统一的行级基线规则，避免单独硬调某一个元素。
