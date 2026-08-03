# Communication Intelligence Foundation

沟通是信任基础设施，而非普通聊天或社区功能。`intelligent_discovery.communication` 只定义领域对象、状态机、审计历史与 Port；不依赖 HTTP、SQLite、模型 SDK 或社区平台。

## 默认隐私与权限边界

`CommunicationRecord` 默认 `private`。沟通内容不能自动转为共享或公开；共享必须经用户授权与现有信任治理流程。风险评估只接收必要元数据（如重复频率、优先级），不得收集、分析或写入私人正文。安全报告和数据权利问题可标为 P0，但仍由人处理。

## 生命周期

`created → received → assigned → processing → (waiting_for_user | resolved) → closed`

状态不可跳跃；每次转换写入 `CommunicationHistory`，包含执行者和理由。P0 为安全/数据权利快速人工响应，P1 为严重缺陷，P2 为功能问题，P3 为普通建议。

## 反馈、求助与贡献

反馈可在处理后形成 `FeedbackResolution`，并可引用已有 `ImprovementProposal`；这只是可追溯关联，不会自动改变系统。受控 Beta 求助通过 `HelpRequestWorkflow` 进入审核、邀请参与、回复、证据复核和人工批准。贡献者提交必须经历证据审核和审核者批准；只有满足全部条件的贡献才**可能**进入既有知识更新治理，模块本身不写知识。

## AI 透明与未来社区

涉及推荐、分析、案例匹配或决策辅助时，应建立 `AIInteractionExplanation`，列出所用信息、来源、假设与不确定性，并保留人工复核。未来可接入 Community、Reputation 和通知适配器；当前没有公共讨论、自动积分、自动处罚或自动知识更新。
