# Intelligent Discovery / 智能发现

> 帮助用户发现信息、学习经验、理解趋势、辅助决策的 AI 知识发现生态。

Intelligent Discovery 是一个长期演进的开放式工程，而不是自动替用户决策的黑箱。每个结论应能回溯到资料来源、置信度和仍然未知的问题。

## 当前能力（v0.1）

实现了可追溯的「发现—研究—分析—报告」闭环：

1. 创建一个发现任务；
2. 为任务登记可审计的资料来源与证据；
3. 对证据形成发现、风险与建议；
4. 保存为可复用知识，并导出 Markdown 报告。

它不替用户做决定。每项结论都关联证据与置信度，并显式记录未知项。

## 工程导航

- [项目总览（建议从这里阅读）](docs/PROJECT_OVERVIEW.md)：一次性查看项目愿景、架构、模块、路线、质量与风险。
- [研究智能基础](docs/RESEARCH_INTELLIGENCE.md)：来源、证据、引用、人工复核与研究失败契约。
- [架构说明](docs/ARCHITECTURE.md)：分层、依赖方向与模块边界。
- [模块与扩展](docs/EXTENSIBILITY.md)：已规划生态能力及接入约束。
- [开发路线](docs/ROADMAP.md)：阶段目标与非目标。
- [架构决策记录](docs/DECISION_LOG.md)：重大取舍的原因与影响。
- [测试记录](docs/TEST_RECORD.md)：质量门禁与最近一次验证。
- [阶段工程报告](docs/reports/2026-08-03-engineering-baseline.md)：当前阶段交付证据。
- [贡献指南](CONTRIBUTING.md)：本地开发、PR 与模块接入规范。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn intelligent_discovery.api:app --reload
```

打开 `http://127.0.0.1:8000/docs` 试用 API。数据库默认位于 `data/intelligent_discovery.db`；可通过 `ID_DATABASE_PATH` 覆盖。

## 边界

v0.1 不内置联网爬取或自动决策。它提供资料登记、分析编排和报告能力；外部搜索、推荐、个人画像、社区等能力通过 `intelligent_discovery.extensions` 的契约后续接入。

## 开源准备状态

项目已经采用 GitHub 协作结构（行为准则、贡献规范、议题与 PR 模板、CI、版本记录）。开源前仍需由项目所有者确认许可证、治理模型、隐私政策及安全响应邮箱，详见 [开源准备清单](docs/OPEN_SOURCE_READINESS.md)。
