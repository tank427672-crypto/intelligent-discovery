# 测试记录

## 质量门禁

每个 PR 至少应通过：

- 单元测试：领域规则、状态转换、证据约束；
- 接口测试：核心 HTTP 闭环与错误语义；
- 静态检查：Ruff；
- 编译检查：`python -m compileall -q intelligent_discovery`。

高风险模块还需要契约、权限、隐私、滥用和性能测试。

## 最近一次记录：2026-08-03（v0.8 Observability + Reliability Intelligence Foundation）

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| Python 版本 | 通过 | Python 3.14.6 |
| 单元/API/契约测试 | 通过 | 17 passed |
| 编译检查 | 通过 | `compileall` 退出码 0 |
| 静态检查 | 通过 | `ruff check .`：All checks passed |

测试覆盖范围：发现任务生命周期、来源归属、来源智能元数据、独立证据与跨任务隔离、人工复核反馈、研究失败语义、案例生命周期、案例版本历史、跨任务案例关联、案例 API、案例提供器契约、知识沉淀、Markdown 报告和 HTTP 闭环。
