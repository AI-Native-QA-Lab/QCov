# Iteration 5 实现过程记录

## 范围

按 `docs/superpowers/plans/2026-09-08-iteration-5-ai-proposal-mapping.md` 落地，
并按双轴审查修复：确定性 offline、错误码、stdin/义务集、`ai.provider`、文档与过程证据。

## RED / GREEN 证据（节选）

### Task 1 marker 评估

```text
$ .venv312/bin/pytest tests/cli/test_markers_eval.py -v
FAILED ... AssertionError: QCOV-CONFIG-001: config must resolve exactly one
obligation and at least one evidence file
# 实现 PytestAdapter.collect 并入评估合并后
$ .venv312/bin/pytest tests/cli/test_markers_eval.py tests/cli/test_map.py -v
8 passed
```

### Task 2 后缀通配

```text
$ .venv312/bin/pytest tests/engine/test_mapping.py::test_apply_mappings_suffix_wildcard_matches_unique_identity -v
FAILED ... assert 0 == 1  (diagnostics QCOV-MAP-001)
# 实现 identity_matches 后
$ .venv312/bin/pytest tests/engine/test_mapping.py -v
11 passed
```

### Task 3–5 Proposal / CLI

```text
ImportError: cannot import name 'QualityProposal' / 'load_proposal' / 'qcov.ai'
# 落地模型、OfflineProvider、CLI 后对应测试转绿
```

## 审查修复后全量门禁

工作目录：`.worktrees/iteration-5`；解释器：`.venv312`（Python 3.12）

```text
.venv312/bin/pytest          → 134 passed
.venv312/bin/ruff check .    → All checks passed
.venv312/bin/mypy qcov       → Success
.venv312/bin/python -m build → Successfully built sdist + wheel
git diff --check             → 通过
```
