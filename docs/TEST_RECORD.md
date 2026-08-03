# 测试记录

## 质量门禁

每个 PR 至少应通过：

- 单元测试：领域规则、状态转换、证据约束；
- 接口测试：核心 HTTP 闭环与错误语义；
- 静态检查：Ruff；
- 编译检查：`python -m compileall -q intelligent_discovery`。

高风险模块还需要契约、权限、隐私、滥用和性能测试。

## 最近一次记录：2026-08-03

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| Python 版本 | 通过 | Python 3.14.6 |
| 单元/API 测试 | 通过 | 4 passed |
| 编译检查 | 通过 | `compileall` 退出码 0 |
| 静态检查 | 通过 | `ruff check .`：All checks passed |

测试覆盖范围：发现任务生命周期、来源归属、非未知结论的证据约束、分析前置条件、知识沉淀、Markdown 报告和 HTTP 闭环。
