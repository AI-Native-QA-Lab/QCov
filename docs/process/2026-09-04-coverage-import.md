# Iteration 1 coverage.py Inventory Import Record

## Scope

Task 3 adds a side-effect-free coverage.py XML reader. It records class-level
identity and line-rate metadata as inventory observations only; it does not
produce a QCov score or obligation-satisfying evidence.

## TDD evidence

The test first failed during collection with
`ModuleNotFoundError: No module named 'qcov.adapters.coverage'`. After the
minimal standard-library XML reader, 2026-09-04 verification passed:

```text
.venv/bin/python -m pytest tests/adapters/test_coverage_adapter.py -q  # 2 passed
.venv/bin/ruff check qcov/adapters tests/adapters                       # passed
.venv/bin/mypy qcov/adapters                                             # passed
git diff --check                                                         # passed
```
