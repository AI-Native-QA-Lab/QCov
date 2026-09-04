# Iteration 1 JUnit Inventory Import Record

## Scope

Task 2 adds a side-effect-free generic JUnit XML reader. It emits inventory
records only and deliberately creates no `QualityEvidence` or inferred
obligation relationship.

## TDD evidence

The focused test first failed during collection with
`ModuleNotFoundError: No module named 'qcov.adapters.junit'`. After the minimal
stdlib XML implementation, 2026-09-04 verification passed:

```text
.venv/bin/python -m pytest tests/adapters/test_junit_adapter.py -q  # 2 passed
.venv/bin/ruff check qcov/adapters tests/adapters                    # passed
.venv/bin/mypy qcov/adapters                                          # passed
git diff --check                                                      # passed
```

Malformed XML yields `QCOV-SCAN-001` as a diagnostic rather than running any
project command or aborting a broader future scan.
