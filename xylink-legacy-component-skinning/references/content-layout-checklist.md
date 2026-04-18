# 内容展示与布局检查清单

> XYLINK 风格迁移不只看颜色、边框和圆角。主文案、help text、error text 和页面节奏同样必须收敛。

## 什么时候必须读这份清单

- 用户提到“内容没显示对”“排版明显不合理”“看起来乱”
- 页面存在长 label、长选项文本、多行说明、error/help text
- 控件在空值、placeholder-only、disabled/read-only 或窄容器下容易出问题

## 一等验收项

- `primary content` 必须可读：已选值、字段 label、错误核心信息、主 CTA 文案
- `secondary content` 可以受限，但不能破坏主信息层级
- 不允许为了显示全文把整排控件、弹窗或卡片无限拉长
- 不允许让 tooltip 成为查看主信息的唯一途径

## 必查案例

- `long label`
- `placeholder-only`
- `long selected value`
- `help text / multi-line help text`
- `error text / inline error`
- `disabled / read-only`
- `narrow container`
- `footer button group`

## 选择处理手段的顺序

1. 合理 `min-width`
2. 局部增宽
3. `panel` 宽于 `trigger`
4. 最多 2 行 `wrap`
5. `ellipsis`

## 失败信号

- 主文案只剩 1-2 个字或难以识别的前缀
- help text / error text 把控件推歪，或与 label 不在一条节奏
- 为了显示全文把整排筛选栏、按钮组或弹窗撑爆
- 只修 token，不检查真实业务内容在页面里的承载结果
