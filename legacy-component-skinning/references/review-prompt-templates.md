# review prompt 模板

> 这些模板用于人工发起 review / 验收 / 补漏回看。按场景复制，替换方括号内容即可。

## 实施补漏 review prompt

适用场景：

- 已经做过一轮换肤，但怀疑默认页之外还有漏检
- 需要继续补齐深层 surface、内容布局和异常态
- 不想进入纯 review，而是继续按实施路径推进

模板：

```text
继续按 legacy-component-skinning 的实施路径处理这个页面，不要先做 review。

范围：
- 页面/路由：[页面或路由]
- 参考源：[设计稿/参考站点/截图]
- 已看过的范围：[默认页、首层弹窗等]
- 怀疑漏检的链路：[编辑 drawer -> 高级 tab -> 二次确认框 / 二级详情页 / step2 等]

这次重点：
- 继续做 interaction sweep，把深层 surface 沿链路展开，不要只停在第一层
- 把 content/layout cases 一起补齐，至少覆盖 long label、help text、error text、多行说明、footer 按钮组、placeholder-only、窄容器
- 把异常态一起回看：[权限不足 / 后端不可用 / 校验失败 / 空数据异常等]

要求：
- 必须更新 manifest，写清 composite surfaces、interactive surfaces、exception states、content/layout cases、breakpoint coverage
- 无法真实回看的页面、状态或断点，必须明确标记为 unverified
- 不要只说“默认页已经差不多”，要明确哪些深层页面和状态已看，哪些还没看
```

## 验收 review prompt

适用场景：

- 已有一轮实现，需要判断能不能对外说“已统一”
- 需要复核共享层收敛、深层页面覆盖和真实观察证据

模板：

```text
按 legacy-component-skinning 的验收路径 review 这次页面调整，判断现在能不能说“已经统一”。

已提供证据：
- 当前 diff：[diff 摘要或直接附 diff]
- 截图/录屏：[happy path / 弹窗 / 其它]
- manifest：[有/无]

请重点检查：
- 是否只看了 happy path，遗漏了编辑后打开的详情页、二级弹窗、step、tab panel、row action 等深层 surface
- 内容展示和页面布局是否真的合理，而不是只看颜色、边框、圆角
- 是否存在应该写进 manifest 但没有写的范围
- 是否有无法真实查看却仍被说成“已通过”的状态

输出要求：
- 明确给出哪些页面、surface、异常态已验证
- 明确给出哪些必须标为 unverified
- 如果证据不足，不要直接给通过结论
```

## 证据不足 review prompt

适用场景：

- 只有 diff、静态代码或少量截图
- 需要方向性判断，但不能冒充完整验收

模板：

```text
我现在只能提供当前 diff 和少量截图，没有完整浏览器回看证据。请按 legacy-component-skinning 先做方向性判断，但不要直接说“已统一/已通过”。

现有材料：
- diff：[摘要]
- 截图：[有哪些]
- 缺失证据：[深层页面 / 异常态 / 某些断点 / 某些二级弹窗]

请你：
- 判断当前改动方向是否合理
- 指出还缺哪些 manifest 项
- 把所有缺少真实渲染证据的页面、surface、异常态、断点明确标记为 unverified
- 明确说明还不能对外宣称完成
```
