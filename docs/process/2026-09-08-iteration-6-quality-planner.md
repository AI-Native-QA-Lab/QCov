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

提交 `42853d8` 前无 `plan` 子命令与 `tests/cli/test_plan.py`。落地后：

```text
$ .venv312/bin/python -m pytest tests/cli/test_plan.py -v
4 passed
```

覆盖：`--config` 多义务计划、config+直接输入拒绝（`QCOV-CLI-003`）、全 COVERED
空 items、`QualityProposal` 不可当 evidence。

## Task 4 文档与全量门禁

更新：`docs/en|zh-CN/concepts.md`、`roadmap.md`、`architecture.md`；`AGENTS.md`；
本过程记录。

2026-09-08（Asia/Shanghai）在本 worktree 实测：

```text
$ .venv312/bin/python -m pytest
149 passed in 7.90s

$ .venv312/bin/ruff check .
All checks passed!

$ .venv312/bin/mypy qcov
Success: no issues found in 37 source files

$ .venv312/bin/python -m build
Successfully built qcov-0.6.0.tar.gz and qcov-0.6.0-py3-none-any.whl

$ git diff --check
（无输出，通过）
```

说明：含 Git 临时仓的用例需完整文件系统权限；沙箱下会出现 diff/snapshot 相关
失败/ERROR，非本迭代回归。
