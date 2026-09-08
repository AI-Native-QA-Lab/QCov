# Iteration 6 设计规格（Quality Planner）

## 范围

撰写规格：
`docs/superpowers/specs/2026-09-08-iteration-6-quality-planner-design.md`。
本记录阶段**无**代码行为变更；实现须另写计划并按 TDD 执行。

## 变更要点

- 纯引擎 `qcov.engine.planner`：固定收益/成本规则表排序 unproven gaps。
- 扩展 `QualityProposal`：`type=quality_plan`、`source.kind=evaluation_gaps`、
  `item.kind=planned_verification`。
- CLI `qcov plan`：`--config` 走多义务评估（对齐 policy）；不扩展 `AIProvider`；
  提案不进 Gap/policy。
- 开发过程文档仅中文；公开 README / CONTRIBUTING / `docs/en|zh-CN` 仍双语。

## 自审修订（2026-09-08）

- 澄清不得复用 `_result_from_inputs`（单义务）；`--config` 对齐 `_policy_bundle`。
- 澄清 `missingEvidenceTypes` 与 Gap Engine「任一 type passed 即 COVERED」语义。
- 补空 `required_types`、禁止 config+直接输入组合、diagnostics 边界。

## 验证

2026-09-08：仅 Markdown。未运行 pytest / ruff / mypy / build。提交前执行
`git diff --check`。
