# World Intelligence Acquisition Foundation

v0.9.5 建立“持续感知世界”的可信输入层，尚不连接真实互联网、不抓取内容、不做 Feed UI，也不发布自动化结论。

## 流程与边界

`SourceRecord → Connector（Port）→ WorldEventCandidate → Evidence → Human Verification → World Event → Discovery Feed`

登记来源不等于来源已验证；来源也不等于证据或知识。连接器只能产生候选，候选必须经历 checking、带证据的人工 verification 后才可 published 并转换为 Feed 项。系统不允许从 discovered 跳到 published。

## 模块

- `source_registry.py`：公开来源、许可、可信等级、更新频率与状态。
- `connector.py`：discover/fetch/parse/verify 适配器契约；未内置 RSS/API/GitHub/arXiv 实现。
- `collector.py`：仅接收已验证来源，并产生不带事实断言的候选。
- `event_candidate.py`、`verification.py`：候选状态机和人工验证边界。
- `freshness.py`：Active / Needs_Update / Archived，不把旧信息伪装为当前信息。
- `trend.py`：可追溯趋势信号，明确不是预测。
- `feed.py`：未来首页与推荐的透明数据输入；不含排序算法或 UI。
- `scheduler.py`：调度契约；不启动后台任务。

## 安全与隐私

该模块只处理公共来源的候选元数据，不接触私人搜索、私人沟通、用户行为或未经授权数据。未来推荐只能使用带证据引用和限制的 `RecommendationSignal`；个人化须由现有授权与数据治理层单独控制。
