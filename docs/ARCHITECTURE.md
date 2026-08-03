# 技术架构

## 项目原则

智能发现是一个帮助用户发现信息、学习经验、理解趋势、辅助决策的 AI 知识发现生态。系统必须保留用户判断权、证据链与不确定性，而非把模型输出当作最终决定。

## 目标与范围

第一阶段验证：用户能否把一个问题变成带来源、结论、风险与下一步的可复用研究报告。

```text
HTTP API / future UI
        │
DiscoveryService ── AnalysisService ── ReportRenderer
        │                    │
SQLite repository       Evidence / finding contracts
        │
Knowledge records
```

领域对象独立于 API 与数据库，未来可替换为消息队列、向量库或图数据库，不改变任务、来源、发现与报告的基础契约。

## 已实现的核心模型

| 模型 | 用途 |
| --- | --- |
| DiscoveryTask | 一个用户问题及其生命周期 |
| Source | 带 URL、摘录、可信度与采集时间的资料 |
| Finding | 基于资料的发现、风险、建议或未知项 |
| KnowledgeRecord | 从已完成任务沉淀的可检索知识 |

## 扩展边界

`extensions.py` 与 `modules.py` 预先定义：

- `ResearchProvider`：外部搜索、数据库、人工研究等资料来源；
- `OpportunitySignalProvider`：未来机会雷达；
- `DecisionAssessmentProvider`：未来决策评估；
- `PersonalizationProvider`：未来个人画像与推荐；
- `ExtensionRegistry`：允许未实现的新模块注册能力声明，避免核心层依赖未来功能；
- `Capability.EXPERIMENTAL`：没有功能的长期插槽，供经过 ADR 评审的新想法安全试验。

## 关键原则

- 结论必须能回溯到至少一个来源。
- 置信度为 0–1，未知项以独立发现保存，而非隐去。
- 自动化能力通过扩展接入；核心服务不假装已完成外部研究。
- 公共接口以向后兼容为默认；破坏性改动需 ADR、迁移路径与主版本升级。
