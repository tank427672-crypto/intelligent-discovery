# Research Intelligence Foundation（v0.2）

## 已实现的基础

### Source Intelligence

来源包含：类型（网页、数据库、API、开源项目、文档、用户提供）、可信等级、可访问状态、许可证信息、采集时间，以及为后续发布/更新时间保留的字段。可信度仍是显式数值，不应由模型凭空生成。

### Evidence Chain

```text
DiscoveryTask → Source → Evidence → Finding → FindingFeedback
```

`Evidence` 保存具体主张、摘录、资料内定位、支持/反驳/上下文关系、验证状态与限制。报告以可追溯引用显示证据。`FindingFeedback` 是人始终在环的最小基础：人工可以接受、拒绝或要求修订，并留下原因。

### Research Provider 契约

`ResearchProvider` 定义 `search`、`fetch`、`parse`、`verify` 四步。它返回 `ResearchResponse`，包含来源、证据和结构化失败；不能以异常吞掉不确定性，更不能用生成内容填补资料缺口。

## 失败处理语义

| 情况 | 标准结果 |
| --- | --- |
| 来源不可访问 | `source_unavailable`，可标注是否可重试。 |
| 数据不足 | `insufficient_data`，不生成确定性结论。 |
| 信息冲突 | `conflicting_information`，保留冲突证据以供人工复核。 |
| 验证失败 | `verification_failed`，不得升级可信度。 |
| 许可证不支持 | `unsupported_license`，不得保存或再利用受限内容。 |

## 未实现项

本版本不含任何真实网页爬取、第三方 API、模型解析或自动验证实现；这些必须作为独立 `ResearchProvider` 接入，在实施前完成来源许可、安全、频率限制、隐私和失败降级评审。

## 迁移与兼容性

SQLite 启动时会以追加列方式迁移现有 `sources` 和 `findings` 表，不删除 v0.1 数据。旧的 `source_ids` 字段仍可读取和写入；新功能优先使用 `evidence_ids`。在 v1 前将提供正式迁移窗口和废弃通知。
