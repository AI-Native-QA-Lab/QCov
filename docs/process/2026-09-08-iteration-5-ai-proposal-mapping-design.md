# Iteration 5 设计规格（映射加固 + AI 提案）

## 范围

撰写规格：
`docs/superpowers/specs/2026-09-08-iteration-5-ai-proposal-mapping-design.md`。
本记录阶段**无**代码行为变更；实现须另写计划并按 TDD 执行。

## 变更要点

- 确认 5a（marker 进评估 + 有限声明式通配）→ 5b（`obligation suggest`）→ 5c（`risk analyze`）。
- 新增 `QualityProposal`（仅 draft）；AIProvider 抽象，默认 `offline`。
- Proposal 不进入 Gap 满足；不改 policy 语义。
- 开发过程文档仅中文；公开 README / CONTRIBUTING / `docs/en|zh-CN` 仍双语。

## 验证

2026-09-08：仅 Markdown。未运行 pytest / ruff / mypy / build。提交前执行
`git diff --check`。
