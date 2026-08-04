# Intelligent Discovery Ecosystem Foundation

v0.9.6 为 Web Beta 预留生态能力，不开放大规模社区、支付、企业服务、移动端或模型绑定。

## 内容与探索

Discovery Stream 支持 Event、Story、Experience、Case、Trend、Knowledge、OpenSource 的统一卡片数据。ContentQualityAssessment 区分 Candidate、Reviewed、Trusted、Featured；Featured 仍必须展示限制，不能表示绝对正确。DiscoveryRelation 连接相关、相似、因果、影响、后续与矛盾关系；已验证关系必须有证据引用。

WorldEventLifecycle 记录 Detected、Emerging、Active、Developing、Resolved、Historical 的顺序变化，并保留来源变化、证据和历史版本链接。

## 生态接口与功能边界

CommunityPort、ExpertNetworkPort、ContributionPort、NotificationPort、AIProviderPort、EnterpriseServicePort、BillingPort 都只是 Port。它们通过 `EcosystemExtensionRegistry` 注册，功能开关默认关闭；注册 Provider 不会自动启用能力。启用必须有人类批准。

所有生态能力的 PermissionBoundary 都禁止修改知识、权限、信誉和规则。贡献、专家增强、通知和模型输出只能产生候选、信号或提案，并沿既有证据、审核、治理和版本流程前进。

## Web Beta 发布门禁

WebBetaReleaseChecklist 需要功能、安全、隐私、版权、备份、恢复、权限、治理和体验九项通过，并且必须记录人工批准者。它不执行部署，也不替代 ReleaseCandidate 的风险、证据与回滚记录。
