# Intelligent Discovery Experience Foundation

本模块为 Web Beta 预备“持续发现”体验的数据与领域基础，不提供 App、页面、无限信息流或注意力优化算法。

## 内容宇宙

`DiscoveryContent` 区分 Event、Story、Experience、Case、Trend、Knowledge 和 OpenSource。它们分别回答“发生了什么、为什么发生、别人经历什么、成败原因、形成中的变化、基础认知、开源项目能做什么”。每条内容必须有来源引用；来源仍不等于证据或验证结论。

## 发现双系统

World Discovery 按世界影响、新鲜度、可信度和趋势信号生成世界范围的 Stream 项，不由个人兴趣主导。Personal Discovery 只接受用户明确确认的兴趣，不读取私人搜索、聊天、正文或未授权行为。两种 Stream 的 `scope` 不可混淆。

## 透明与控制

推荐必须提供 `RecommendationExplanation`：原因、证据引用与限制缺一不可。InterestProfile 是可查看、修改、删除的兴趣信号，不是身份或隐藏画像。Following 仅允许关注公开的人、专家、项目、公司或主题，更新不能暴露私人行为。

## 价值和精选

DiscoveryValue 衡量理解、收藏、探索、问题解决与贡献，不衡量停留时间。Featured Discovery 是人工精选，`verified=False` 时必须保留候选/未验证语义；精选不改变证据链要求。

## 开发者联系

Communication Gateway 将产品反馈、Bug、安全报告、案例贡献和合作请求转为默认私有的 CommunicationRecord。安全报告为 P0，其他请求进入既有沟通、审计与治理流程。
