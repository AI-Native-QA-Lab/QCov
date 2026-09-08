# Iteration 4 策略与豁免

## TDD 证据

- RED：严格策略模型测试最初因旧 `QualityPolicy` 仍要求 `policies` 而失败；GREEN：`.venv/bin/pytest tests/models/test_protocol.py tests/models/test_io.py -q` 通过 `6 passed`。
- RED：`.venv/bin/pytest tests/engine/test_policy.py -q` 因缺少 `qcov.engine.policy` 失败；GREEN：该套件通过 `4 passed`，覆盖 BLOCK、有效豁免、到期边界和排序。
- RED：`.venv/bin/pytest tests/engine/test_policy_reports.py -q` 因缺少 renderer 失败；GREEN：报告和 catalog 聚焦套件通过 `3 passed`。
- RED：CLI 测试在 `policy` 子命令不存在时退出码为 2；GREEN：单义务中文 WARN 测试通过。
- 全量测试首次发现两个 `test_policy.py` 的收集冲突，已将 CLI 测试命名为 `test_policy_command.py`。

## 最终验证

2026-09-07：`.venv/bin/pytest -q` 通过 `87 passed`；`.venv/bin/ruff check .` 与 `.venv/bin/mypy qcov` 通过。首次隔离构建受沙箱 DNS 限制无法下载 hatchling；获准重试后 `.venv/bin/python -m build` 成功生成 `qcov-0.3.0.tar.gz` 与 `qcov-0.3.0-py3-none-any.whl`。`git diff --check` 通过。

## 范围

本迭代实现 `qcov policy check` 的本地策略评估、显式 `--as-of`、默认允许状态、精确时限豁免、PASS/WARN/BLOCK、稳定 JSON 和中英文 Markdown。未实现 DSL、维度阈值、通配符、远程 Git、数据库与 AI 决策。
