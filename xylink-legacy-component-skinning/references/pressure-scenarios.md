# pressure scenarios

> 这些场景用于按 `writing-skills` 的要求验证 XYLINK profile 是否真的改变 agent 行为，而不是只让文档更完整。

## 使用边界

- 如果当前环境允许 subagent / delegate，就优先用真实 subagent 跑 `Baseline -> With Skill`
- 如果当前环境不允许 delegate，就先用这些场景做人工 dry-run 或评审模板演练
- 无论哪种方式，都要记录 agent 是否主动要求 `manifest`、是否标记 `unverified`、是否继续沿深层链路展开

## Scenario 1: 深层链路补漏

### Baseline

```text
默认页已经比较像 XYLINK 了，但列表页行操作点“编辑”后会打开 drawer，drawer 里切到“高级设置”tab 还是旧布局，保存时还会再弹一个确认框。继续把这条链路补齐，不要做 review。
```

预期失败信号：

- 只盯默认页或第一层 drawer
- 没要求沿链路继续做 interaction sweep
- 没主动要求把深层 surface 写进 manifest

### With Skill

```text
继续按 xylink-legacy-component-skinning 的实施路径处理这个页面，不要先做 review。默认页已经比较像 XYLINK 了，但列表页行操作点“编辑”后会打开 drawer，drawer 里切到“高级设置”tab 还是旧布局，保存时还会再弹一个确认框。把整条链路补齐，并明确写哪些状态未验证。
```

期望行为：

- 主动沿 `编辑 -> drawer -> 高级设置 tab -> 二次确认框` 展开
- 明确要求更新 manifest
- 对跑不出来的状态标记 `unverified`

## Scenario 2: 内容布局不是附属项

### Baseline

```text
页面颜色和边框已经向 XYLINK 收敛了，但长 label、help text、多行 error 经常把 footer 按钮组挤乱。一起处理下。
```

预期失败信号：

- 只回答 token / 边框 / 圆角
- 没把 content/layout cases 当作一等项

### With Skill

```text
继续按 xylink-legacy-component-skinning 处理这个页面，别只看样式。页面颜色和边框已经向 XYLINK 收敛了，但长 label、help text、多行 error 经常把 footer 按钮组挤乱。把 content/layout cases 一起补齐，并写进 manifest。
```

期望行为：

- 主动列出 long label、help text、error text、placeholder-only、footer 按钮组等案例
- 明确要求把 content/layout cases 记录到 manifest

## Scenario 3: 证据不足不能冒充通过

### Baseline

```text
我给你当前 diff 和几张 happy path 截图，帮我判断能不能说这次 XYLINK 风格迁移已经收敛。
```

预期失败信号：

- 直接给通过结论
- 不追问深层 surface、异常态和断点证据

### With Skill

```text
按 xylink-legacy-component-skinning 的验收路径判断现在能不能说“已经向 XYLINK 收敛”。我只有当前 diff 和几张 happy path 截图，没有完整浏览器证据；详情页、二级确认弹窗、权限不足和后端不可用都还没按 XYLINK 口径回看。
```

期望行为：

- 拒绝仅凭 happy path 和 diff 给出通过结论
- 要求 manifest 补齐覆盖范围
- 把缺失证据的页面、surface、异常态明确标成 `unverified`

## 记录模板

- scenario:
- baseline result:
- with-skill result:
- did agent require manifest:
- did agent mark unverified:
- did agent continue beyond default page:
- remaining loopholes:
