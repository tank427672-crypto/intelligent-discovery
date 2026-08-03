# Case Intelligence Foundation（v0.3）

## 目标与边界

案例是长期知识资产，不是普通内容。本阶段实现“人工或受控来源录入 → 追溯验证 → 版本化跟踪 → 跨任务复用”的基础；不实现自动发现、自动分析、社区发布或贡献积分。

## 案例模型

`CaseRecord` 包含案例名称、类型、背景、问题、解决方案、结果、成功/失败因素、经验、适用范围、限制、来源/证据/发现关联、许可证、验证状态、可信度、版本和时间。

```text
Origin DiscoveryTask
        ↓
Source → Evidence → Finding
        ↓
    CaseRecord → CaseRevision
        ↓
 CaseTaskLink → other DiscoveryTask / report
```

案例创建时必须引用来源，且所有证据和发现都必须属于它的原始任务。跨任务复用只通过 `CaseTaskLink` 进行，避免把不同任务的证据混在一起。

## 生命周期与验证

```text
candidate → tracked → verified → mature → historical
```

进入 `verified` 或 `mature` 前，案例验证状态必须为 `verified`。验证状态还可以明确为 `pending`、`disputed` 或 `rejected`。生命周期与正文更新都会新建版本历史，旧版本不会覆盖。

## 未来接口（未实现）

- `CaseDiscoveryProvider`：仅返回候选案例与局限，不能直接创建验证案例。
- `CaseVerificationProvider`：核查来源真实性、许可证和证据。
- `CaseAnalysisProvider`：生成可追溯的分析草稿，须经人工复核。
- `CaseUpdateProvider`：跟踪现实变化，作为后续版本输入。

任何实现必须遵守 ResearchProvider 的来源许可和失败语义，并补齐 ADR、契约测试、隐私/滥用评审。
