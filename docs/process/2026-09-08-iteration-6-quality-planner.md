# Iteration 6 实现过程记录

## 范围

按 `docs/superpowers/plans/2026-09-08-iteration-6-quality-planner.md` 落地确定性
Quality Planner（`qcov plan` → draft `quality_plan`），并更新双语公开文档、
`AGENTS.md` 与全量门禁。工作目录：`.worktrees/iteration-6`；解释器：
`.venv312`（Python 3.12）。

相关提交：

| Commit | 说明 |
| --- | --- |
| `1c2012c` | 扩展 QualityProposal 枚举（`quality_plan` / `evaluation_gaps` / `planned_verification`） |
| `a2c39ca` | 确定性 planner 引擎 |
| `cf82a62` | planner tie-break 单测 |
| `42853d8` | `qcov plan` CLI |

## RED / GREEN 证据

### Task 1 协议枚举

复现 RED（临时回退 `qcov/models/protocol.py` 至 `1c2012c^`）：

```text
$ .venv312/bin/python -m pytest \
    tests/models/test_protocol.py::test_quality_proposal_accepts_quality_plan -v
FAILED ... ValidationError: 3 validation errors for QualityProposal
```

GREEN（恢复后 / 提交 `1c2012c` 起）：

```text
$ .venv312/bin/python -m pytest \
    tests/models/test_protocol.py::test_quality_proposal_accepts_quality_plan \
    tests/models/test_io.py -v
8 passed
```

### Task 2 planner 引擎

复现 RED（临时移走 `qcov/engine/planner.py`）：

```text
$ .venv312/bin/python -m pytest \
    tests/engine/test_planner.py::test_planner_orders_by_priority_score -v
ERROR ... ModuleNotFoundError: No module named 'qcov.engine.planner'
```

GREEN（提交 `a2c39ca` + `cf82a62`）：

```text
$ .venv312/bin/python -m pytest tests/engine/test_planner.py -v
9 passed
```

### Task 3 CLI `qcov plan`

RED（实现前无 `plan` 子命令；复现：检出 `42853d8^` 并保留当前 `tests/cli/test_plan.py`，或在空命令表上 invoke）：

```text
$ .venv312/bin/python -c "from typer.testing import CliRunner; from qcov.cli.app import app; \
  r=CliRunner().invoke(app, ['plan', '--help']); print(r.exit_code, r.output[:200])"
# 实现前：exit_code != 0，提示 No such command 'plan'
```

GREEN（提交 `42853d8` 起；审查修复后含 locale 测）：

```text
$ .venv312/bin/python -m pytest tests/cli/test_plan.py -v
5 passed
```

覆盖：`--config` 多义务计划、`--locale zh-CN` markdown 文案、config+直接输入拒绝
（`QCOV-CLI-003`）、全 COVERED 空 items、`QualityProposal` 不可当 evidence。

## Task 4 文档与全量门禁

更新：`docs/en|zh-CN/concepts.md`、`roadmap.md`、`architecture.md`；`AGENTS.md`；
本过程记录。

## 审查修复（2026-09-09）

对照 `main...HEAD` 双轴审查后修复：

- README / requirements 双语补齐 Iteration 6 / `qcov plan`
- `plan --locale` 影响 markdown summary 语言
- 非法 `quality_plan` 枚举拒绝单测
- 抽取 `qcov.models.proposal_ids`；`_multi_obligation_evaluation` 避免 plan 双载

```text
$ .venv312/bin/python -m pytest
# 见下方全量门禁
```

2026-09-09（Asia/Shanghai）审查修复后全量门禁：

```text
$ .venv312/bin/python -m pytest
151 passed in 8.34s

$ .venv312/bin/ruff check .
All checks passed!

$ .venv312/bin/mypy qcov
Success: no issues found in 38 source files

$ .venv312/bin/python -m build
Successfully built qcov-0.6.0.tar.gz and qcov-0.6.0-py3-none-any.whl

$ git diff --check
（无输出，通过）
```

2026-09-08（Asia/Shanghai）初版门禁：

```text
$ .venv312/bin/python -m pytest
149 passed in 7.90s
```

说明：含 Git 临时仓的用例需完整文件系统权限；沙箱下会出现 diff/snapshot 相关
失败/ERROR，非本迭代回归。
