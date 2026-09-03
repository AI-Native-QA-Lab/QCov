# Evidence Gap Engine Implementation Record

## Scope

Task 3 of the MVP plan implements a pure evaluator for explicit Testing
Obligations and Quality Evidence. It intentionally performs no test inference,
quality scoring, or policy decision.

## Test-first record

The first engine test was run before the engine module existed and failed with
`ModuleNotFoundError: No module named 'qcov.engine'`. The final test set covers
fully covered, partially covered, fully missing, and mixed unknown/missing
dimension states.

## Verification

2026-09-03 (Asia/Shanghai):

```text
.venv/bin/python -m pytest tests/engine/test_gaps.py -q  # 4 passed
.venv/bin/ruff check qcov/engine tests/engine            # passed
.venv/bin/mypy qcov/engine                               # passed
git diff --check                                          # passed
```

The evaluator treats only passed evidence with the exact obligation reference,
dimension, and allowed type as covering evidence. Failed/skipped evidence does
not satisfy a requirement; unknown observations remain visibly unproven.
