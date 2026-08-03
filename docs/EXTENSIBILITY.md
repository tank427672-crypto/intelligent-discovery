# 模块化与扩展设计

## 依赖规则

```text
interfaces (HTTP / CLI / UI) → application services → core domain
                                      ↓
                                  ports (Protocol)
                                      ↑
                       infrastructure / extensions
```

核心领域不得引用 FastAPI、SQLite、模型 SDK 或任何未来模块。应用服务只引用端口；基础设施负责实现端口。这样可以测试核心逻辑、替换存储，也使社区插件不侵入核心。

## 能力目录

| 模块 | 能力键 | 当前状态 | 关键约束 |
| --- | --- | --- | --- |
| Discovery Core | `research` | v0.1 | 结论可追溯到证据 |
| Opportunity Radar | `opportunity_discovery` | 预留 | 信号来源与时效必须可审计 |
| Decision Analysis | `decision_analysis` | 预留 | 只能辅助，不替代用户决策 |
| Personal Intelligence | `personal_intelligence` | 预留 | 明示同意、最小化数据 |
| Recommendation | `recommendation` | 预留 | 可解释、可关闭、可反馈 |
| Case Intelligence | `case_intelligence` | 预留 | 案例来源、匿名化、适用边界 |
| Community | `community` | 预留 | 审核、举报、版本归属 |
| Contribution | `contribution` | 预留 | 抗刷、可申诉、可审计 |
| Enterprise | `enterprise` | 预留 | 租户隔离、权限、审计 |
| Experimental | `experimental` | 长期预留 | ADR 审核后才可稳定化 |

## 插件生命周期

1. 在 Issue 阐明问题、用户价值、数据与风险。
2. 使用现有 `Capability` 或提出 ADR 扩展新能力。
3. 在独立实现中满足 `Protocol`，通过 `ExtensionRegistry` 注册。
4. 提供契约测试、失败降级、日志和最小权限设计。
5. 试验期收集反馈；稳定后再纳入公开兼容性承诺。
