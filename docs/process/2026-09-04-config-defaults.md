# Iteration 1 Config Defaults Record

## Scope

Task 5 adds `--config` defaults to `gaps`, `check`, and `report`. Explicit
`--obligation` plus `--evidence` remains the highest-priority input path.

## TDD evidence

The config-default command test first failed with exit code 2 because `gaps`
did not accept `--config`. After shared input resolution was implemented,
2026-09-04 verification passed:

```text
.venv/bin/python -m pytest tests/cli/test_commands.py -q  # 6 passed
.venv/bin/ruff check qcov/cli tests/cli                   # passed
.venv/bin/mypy qcov/cli                                   # passed
git diff --check                                           # passed
```

Configuration must resolve exactly one obligation and at least one evidence
file. Otherwise QCov returns `QCOV-CONFIG-001`; it never chooses an arbitrary
obligation or silently evaluates no evidence.
