# Knowledge Graph + Decision Intelligence Foundation（v0.4）

## 已实现

`Concept` 表示命名知识概念；`Relationship` 连接 Source、Evidence、Finding、KnowledgeRecord、CaseRecord 和 Concept。关系必须引用已存在的节点，且可附加证据 ID；系统不自动猜测关系。

案例相似度是一个透明的基础查询：两个案例只有在它们显式连接到同一 Concept 时才被视为相似，结果按共享概念数量排序。它不是语义模型推荐，也不表示案例适用性或成功概率。

`ReflectionRecord` 保存原始判断、现实结果、偏差、原因分析与经验更新，并只允许关联案例原始任务的证据。

## 决策边界

`DecisionContext` 与 `DecisionAnalysisProvider` 仅定义未来可解释比较的输入/输出。当前没有决策评分、自动推荐或预测实现。未来输出必须包含选项、证据、风险、未知项、限制和 `requires_human_review`。

## 风险

图谱当前为显式人工/受控提供器录入，不含实体消歧、全局搜索、权限隔离或图算法。关系质量取决于证据与人工复核；无证据关系必须被视为弱关联而非事实。
