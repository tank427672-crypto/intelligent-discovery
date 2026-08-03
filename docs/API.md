# API 约定（v0.1）

交互式 API 文档在启动服务后位于 `/docs`。当前资源：

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/tasks` | 创建发现任务，状态进入 `researching` |
| `POST` | `/tasks/{id}/sources` | 录入可审计资料 |
| `POST` | `/tasks/{id}/findings` | 录入发现、风险、建议或未知项 |
| `POST` | `/tasks/{id}/analyze` | 验证资料后进入分析状态 |
| `POST` | `/tasks/{id}/complete` | 沉淀知识记录 |
| `GET` | `/tasks/{id}/report` | 输出 Markdown 报告 |
| `GET` | `/knowledge` | 列出已沉淀知识 |

## 兼容性策略

`/v1` 路由将在第一个稳定公开 API 发布时引入。v0.x 中仍会改进接口，但会在 `CHANGELOG.md` 和迁移说明中记录。未来的插件 API 与 HTTP API 分开版本化。
