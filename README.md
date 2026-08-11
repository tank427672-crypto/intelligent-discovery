# Intelligent Discovery / 智能发现

> 帮助用户发现信息、学习经验、理解趋势、辅助决策的 AI 知识发现生态。

Intelligent Discovery 是一个长期演进的开放式工程，而不是自动替用户决策的黑箱。每个结论应能回溯到资料来源、置信度和仍然未知的问题。

本项目采用 [Apache License 2.0](LICENSE)。

## 当前能力（v0.9.1 Beta Preparation）

实现了可追溯的「发现—研究—分析—报告」闭环：

1. 创建一个发现任务；
2. 为任务登记可审计的资料来源与证据；
3. 对证据形成发现、风险与建议；
4. 保存为可复用知识，并导出 Markdown 报告。

它不替用户做决定。每项结论都关联证据与置信度，并显式记录未知项。

## 工程导航

- [项目总览（建议从这里阅读）](docs/PROJECT_OVERVIEW.md)：一次性查看项目愿景、架构、模块、路线、质量与风险。
- [研究智能基础](docs/RESEARCH_INTELLIGENCE.md)：来源、证据、引用、人工复核与研究失败契约。
- [案例智能基础](docs/CASE_INTELLIGENCE.md)：案例资产、版本、验证、跨任务关联与未来插件边界。
- [知识图谱与决策基础](docs/KNOWLEDGE_GRAPH.md)：概念、证据关系、反思与决策契约边界。
- [智能发现检索基础](docs/DISCOVERY_INTELLIGENCE.md)：本地搜索、目录、分类、反馈与受限推荐边界。
- [信任、治理与演进基础](docs/TRUST_GOVERNANCE.md)：可见性、审核、功能反馈和人工批准的演进边界。
- [架构说明](docs/ARCHITECTURE.md)：分层、依赖方向与模块边界。
- [模块与扩展](docs/EXTENSIBILITY.md)：已规划生态能力及接入约束。
- [开发路线](docs/ROADMAP.md)：阶段目标与非目标。
- [架构决策记录](docs/DECISION_LOG.md)：重大取舍的原因与影响。
- [测试记录](docs/TEST_RECORD.md)：质量门禁与最近一次验证。
- [阶段工程报告](docs/reports/2026-08-03-engineering-baseline.md)：当前阶段交付证据。
- [Beta 测试说明](BETA.md)：测试用户边界、反馈入口与处理路径。
- [案例种子与展示指南](CASE_GUIDE.md)：候选案例、版权和人工导入门槛。
- [发布计划](RELEASE_PLAN.md)：Alpha 到 Beta 的人工发布门禁。
- [沟通智能基础](docs/COMMUNICATION_INTELLIGENCE.md)：私有沟通、反馈处理、受控求助和 AI 解释边界。
- [Beta 体验智能](docs/BETA_EXPERIENCE_INTELLIGENCE.md)：隐私优先的体验信号、反馈闭环与受控进化。
- [世界智能获取基础](docs/WORLD_INTELLIGENCE.md)：公共来源、候选事件、新鲜度、趋势与可信 Feed 输入边界。
- [发现体验基础](docs/DISCOVERY_EXPERIENCE.md)：内容宇宙、世界/个人发现隔离、兴趣与透明推荐边界。
- [生态与 Web Beta 候选基础](docs/ECOSYSTEM_FOUNDATION.md)：默认关闭的生态接口、权限边界与发布门禁。
- [贡献指南](CONTRIBUTING.md)：本地开发、PR 与模块接入规范。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn intelligent_discovery.api:app --reload
```

打开 `http://127.0.0.1:8000/docs` 试用 API。数据库默认位于 `data/intelligent_discovery.db`；可通过 `ID_DATABASE_PATH` 覆盖。

## Beta 边界

案例种子仅用于展示和人工研究准备，尚未导入为已验证知识。测试用户可以通过 API 浏览候选和提交反馈，但公开发布、自动决策、自动治理、自动积分及自动处罚均未实现。

## 开源准备状态

项目已经采用 GitHub 协作结构（行为准则、贡献规范、议题与 PR 模板、CI、版本记录）。开源前仍需由项目所有者确认许可证、治理模型、隐私政策及安全响应邮箱，详见 [开源准备清单](docs/OPEN_SOURCE_READINESS.md)。
