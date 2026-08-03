# 测试记录

## 质量门禁

每个 PR 至少应通过：

- 单元测试：领域规则、状态转换、证据约束；
- 接口测试：核心 HTTP 闭环与错误语义；
- 静态检查：Ruff；
- 编译检查：`python -m compileall -q intelligent_discovery`。

高风险模块还需要契约、权限、隐私、滥用和性能测试。

## 最近一次记录：2026-08-03（v0.9.1 Beta Release Preparation + Case Showcase Foundation）

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| Python 版本 | 通过 | Python 3.14.6 |
| 单元/API/契约测试 | 通过 | 26 passed（1 条第三方弃用警告） |
| 编译检查 | 通过 | `compileall` 退出码 0 |
| 静态检查 | 通过 | `ruff check .`：All checks passed |

测试覆盖范围：既有发现/研究/案例/图谱/治理闭环，以及案例候选导入、许可证声明、展示契约、Beta 反馈权限与分诊、发布检查清单和反馈事件最小化记录。
