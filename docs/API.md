# API 约定（v0.2）

交互式 API 文档在启动服务后位于 `/docs`。当前资源：

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/tasks` | 创建发现任务，状态进入 `researching` |
| `POST` | `/tasks/{id}/sources` | 录入可审计资料 |
| `POST` | `/tasks/{id}/evidence` | 绑定资料来源的可定位证据 |
| `POST` | `/tasks/{id}/findings` | 录入发现、风险、建议或未知项 |
| `POST` | `/tasks/{id}/feedback` | 保存人工复核反馈 |
| `POST` | `/tasks/{id}/analyze` | 验证资料后进入分析状态 |
| `POST` | `/tasks/{id}/complete` | 沉淀知识记录 |
| `GET` | `/tasks/{id}/report` | 输出 Markdown 报告 |
| `GET` | `/knowledge` | 列出已沉淀知识 |

## 兼容性策略

`/v1` 路由将在第一个稳定公开 API 发布时引入。v0.x 中仍会改进接口，但会在 `CHANGELOG.md` 和迁移说明中记录。未来的插件 API 与 HTTP API 分开版本化。

## 证据与人工复核

`Source` 记录资料，`Evidence` 记录资料中具体支持、反驳或补充判断的可定位摘录。`Finding` 可引用 `evidence_ids`；v0.1 的 `source_ids` 暂时兼容。非未知发现不能没有来源或证据。

`Feedback` 只记录人工复核结论、理由和非敏感角色标签，不要求或建议写入个人身份信息。
