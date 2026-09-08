# Iteration 4 后路线图修订

## 范围

文档与治理对齐：双语 `docs/en|zh-CN/roadmap.md`、`requirements.md`、`AGENTS.md`，
以及规格说明 `docs/superpowers/specs/2026-09-08-post-iteration-4-roadmap-revision.md`。
无代码行为变更。

## 变更要点

- 记录 Iteration 0–4 已交付能力，并补齐中文路线图中的 Iteration 3。
- 将下一优先项定为 Iteration 4.5：显式义务映射 + 真实项目验证。
- Iteration 5–7 AI 与 Iteration 8 生产证据保持其后，且 AI 不得成为证据/门禁权威。
- 需求页区分核心引擎、已交付本地能力、仍排除项、待补映射。
- `AGENTS.md` 不再把已交付的 `diff` / `policy` 写成默认禁止项。

## 验证

2026-09-08：本修订仅改 Markdown / `AGENTS.md`。未运行 pytest / ruff / mypy / build，
因为无 Python 行为变更。`git diff --check` 应在提交前执行。
