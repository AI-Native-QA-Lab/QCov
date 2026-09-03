# Refund Reference Example Record

## Scope

Task 5 adds an executable financial-refund obligation. It proves behavior,
boundary, and data evidence while intentionally leaving concurrency, idempotency,
and production unproven.

## Test-first and verification record

The reference-fixture test was run before the files existed and failed with a
stable `QCOV-SCHEMA-001` file-loading error. After fixture creation, 2026-09-03
(Asia/Shanghai) checks passed:

```text
.venv/bin/python -m pytest tests/examples/test_refund_data.py -q  # 1 passed
.venv/bin/ruff check examples tests/examples                       # passed
.venv/bin/mypy tests/examples                                      # passed
git diff --check                                                    # passed
```
