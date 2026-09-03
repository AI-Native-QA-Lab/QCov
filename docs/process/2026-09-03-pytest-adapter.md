# pytest Reference Adapter Record

## Scope

Task 7 delivers an AST-only reference adapter. It recognizes the explicit
literal marker `@pytest.mark.qcov("QO-...")` and emits an unknown evidence
record. It does not execute tests, infer obligation mappings, or claim a pass.

## Test-first and verification record

The adapter tests initially failed because `qcov.adapters` did not exist. On
2026-09-03 (Asia/Shanghai), the following checks passed:

```text
.venv/bin/python -m pytest tests/adapters/test_pytest_adapter.py -q  # 2 passed
.venv/bin/ruff check qcov/adapters tests/adapters                    # passed
.venv/bin/mypy qcov/adapters                                          # passed
```
