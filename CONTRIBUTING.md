# Contributing

感谢你帮助建设 Intelligent Discovery。贡献必须服务于项目原则：帮助用户发现信息、学习经验、理解趋势、辅助决策；不得把不可解释的自动结论伪装为事实或决定。

## 本地开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
ruff check .
```

## 贡献流程

1. 先在 Issue 中描述问题、受益用户、非目标与风险。
2. 一项 PR 只解决一个可审核的目标，并同步更新测试、文档和 `CHANGELOG.md`。
3. 不破坏已发布 API；若必须破坏，先提出 ADR 并走主版本升级流程。
4. 涉及个人数据、推荐、评分、积分或企业数据的改动，必须补充隐私/滥用风险与人工复核设计。

## 新模块接入

- 不得让核心领域层直接依赖外部服务 SDK。
- 在 `extensions.py` 定义或复用能力契约；实现放在基础设施或独立包中。
- 通过 `ExtensionRegistry` 注册，写明输入、输出、失败行为、权限与可观测性。
- 新能力先以实验性模块进入；稳定后才写入公共接口。

## 提交约定

推荐 Conventional Commits：`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`。提交不得包含密钥、真实个人资料或未授权资料。
