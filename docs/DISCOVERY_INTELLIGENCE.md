# Discovery Intelligence Foundation（v0.5）

## 已实现

Discovery Search 只检索本地的 Concept、Case、Finding 与 KnowledgeRecord，返回摘要、关系、分类和明确限制；不会假装覆盖互联网，也不调用模型生成答案。

Discovery Catalog 提供 Category（支持父级）和 Tag；Classification 保存对象、分类、置信度、分类来源和审核状态。AI 分类只能作为 `ai_suggestion`，默认必须等待人工确认。

SearchQuery 与 SearchFeedback 保存搜索及结果是否有用的反馈。RecommendationRecord 只允许记录理由、证据、案例与反馈；不提供自动排序或商业广告推荐。

## 预留且未开放

PersonalDiscoverySpace 必须有显式授权；HelpRequest 和 CommunityContribution 只是数据模型/契约，未开放社区提交。自动分类、推荐、趋势、个人仪表盘和社区排序均未实现。

## 风险

当前搜索使用 SQLite `LIKE`，不支持全文检索、权限隔离、拼写纠错、语义检索或大规模排序。分类、推荐和反馈的治理、删除权和防滥用规则需要在接入真实用户数据前由架构负责人决策。
