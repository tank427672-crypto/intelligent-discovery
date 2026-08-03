# 测试记录

## 质量门禁

每个 PR 至少应通过：

- 单元测试：领域规则、状态转换、证据约束；
- 接口测试：核心 HTTP 闭环与错误语义；
- 静态检查：Ruff；
- 编译检查：`python -m compileall -q intelligent_discovery`。

高风险模块还需要契约、权限、隐私、滥用和性能测试。

## 最近一次记录：2026-08-03（v0.9.2 Trust Foundation + Private Beta Operations）

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| Python 版本 | 通过 | Python 3.14.6 |
| 单元/API/契约测试 | 通过 | 36 passed（1 条第三方弃用警告） |
| 编译检查 | 通过 | `compileall` 退出码 0 |
| 静态检查 | 通过 | `ruff check .`：All checks passed |

测试覆盖范围：既有发现/研究/案例/图谱/治理闭环、案例候选与 Beta 反馈、RC 顺序审批、数据导出/删除/审计、非破坏性备份恢复、协议/同意/退出、案例审核门槛，以及私有沟通生命周期、反馈结案、求助/贡献边界与 AI 解释。
