# API 约定（v0.3）

交互式 API 文档在启动服务后位于 `/docs`。当前资源：

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/tasks` | 创建发现任务，状态进入 `researching` |
| `POST` | `/tasks/{id}/sources` | 录入可审计资料 |
| `POST` | `/tasks/{id}/evidence` | 绑定资料来源的可定位证据 |
| `POST` | `/tasks/{id}/findings` | 录入发现、风险、建议或未知项 |
| `POST` | `/tasks/{id}/feedback` | 保存人工复核反馈 |
| `POST` | `/cases` | 创建有来源、证据和版本历史的案例资产 |
| `GET` | `/cases` | 查询案例，可按任务关联过滤 |
| `GET` | `/cases/{id}` | 读取案例及其版本历史 |
| `PATCH` | `/cases/{id}` | 通过变更原因更新案例并生成新版本 |
| `POST` | `/cases/{id}/lifecycle/{status}` | 严格推进案例生命周期 |
| `POST` | `/cases/{id}/links` | 将案例关联到另一个发现任务 |
| `POST` | `/tasks/{id}/analyze` | 验证资料后进入分析状态 |
| `POST` | `/tasks/{id}/complete` | 沉淀知识记录 |
| `GET` | `/tasks/{id}/report` | 输出 Markdown 报告 |
| `GET` | `/knowledge` | 列出已沉淀知识 |

## 兼容性策略

`/v1` 路由将在第一个稳定公开 API 发布时引入。v0.x 中仍会改进接口，但会在 `CHANGELOG.md` 和迁移说明中记录。未来的插件 API 与 HTTP API 分开版本化。

## 证据与人工复核

`Source` 记录资料，`Evidence` 记录资料中具体支持、反驳或补充判断的可定位摘录。`Finding` 可引用 `evidence_ids`；v0.1 的 `source_ids` 暂时兼容。非未知发现不能没有来源或证据。

`Feedback` 只记录人工复核结论、理由和非敏感角色标签，不要求或建议写入个人身份信息。

## 案例资产

案例必须引用其原始发现任务中的至少一个来源；可进一步关联证据与发现。案例正文保存摘要、分析和经验，不保存受版权保护的完整原文。每次内容或生命周期变化都会生成 `CaseRevision`；案例可以通过明确关系被引用到其他任务。
