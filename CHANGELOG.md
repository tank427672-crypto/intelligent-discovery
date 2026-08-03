# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/) 的记录方式，并计划在发布后采用语义化版本。

## [Unreleased]

## [0.2.0] - 2026-08-03

### Added

- 来源智能元数据：来源类型、可信等级、可访问状态与许可证信息。
- 独立 `Evidence` 与 `FindingFeedback` 对象，建立来源—证据—发现—人工反馈链。
- 研究提供器统一契约，以及不可访问、数据不足、信息冲突、验证失败和许可不支持的结构化失败语义。
- 证据、反馈 API 及带证据链/人工复核的 Markdown 报告。

### Changed

- SQLite 数据库在启动时为现有来源和发现表做非破坏性列迁移。

### Added

- GitHub 长期协作治理文件、质量门禁与阶段工程报告。
- 面向未来生态模块的能力目录与稳定扩展契约。
- 应用服务对持久化端口的依赖，支持替换 SQLite 实现。

## [0.1.0] - 2026-08-03

### Added

- 发现任务、证据来源、发现记录、知识沉淀与 Markdown 报告闭环。
- FastAPI HTTP 接口及核心/API 回归测试。
