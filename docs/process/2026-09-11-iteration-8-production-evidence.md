# Iteration 8：Production Evidence 过程记录

## 范围

增加本地 `ProductionObservationReport` 与 `production-observation` adapter；生产观察只经显式 mapping 成为证据，且 observation 时间戳为执行时间权威。

设计：`docs/superpowers/specs/2026-09-11-iteration-8-production-evidence-design.md`
计划：`docs/superpowers/plans/2026-09-11-iteration-8-production-evidence.md`

## TDD 记录

- RED：生产模型/adapter 不存在，pytest collection 报 `ImportError` / `ModuleNotFoundError`。
- GREEN：模型与 adapter 聚焦测试 15 passed；config/registry/scan 测试 14 passed；mapping 测试 12 passed。
- RED：生产 mapping producer 被协议拒绝；GREEN：显式 production mapping 保留 observation timestamp。
- RED：新增公开页面和 README 链接测试失败；GREEN：文档测试 5 passed。

## 最终验证（2026-09-11）

```text
PYTHONPATH=. ../../.venv/bin/pytest -q
183 passed in 10.63s

PYTHONPATH=. ../../.venv/bin/ruff check .
All checks passed!

PYTHONPATH=. ../../.venv/bin/mypy qcov
Success: no issues found in 43 source files

PYTHONPATH=. ../../.venv/bin/python -m build
Successfully built qcov-0.8.0.tar.gz and qcov-0.8.0-py3-none-any.whl
```

首次 build 因沙箱 DNS 无法下载 hatchling；获准在受控构建命令重试后通过。
