# Reporting and Internationalization Record

## Scope

Task 4 adds presentation-only localization and JSON/Markdown reporting. Protocol
keys and enum values remain English in JSON; Markdown uses `en` or `zh-CN` labels.

## Test-first and verification record

Before implementation, report/catalog imports failed because neither module
existed. On 2026-09-03 (Asia/Shanghai), the following checks passed:

```text
.venv/bin/python -m pytest tests/engine/test_reports.py tests/i18n/test_catalog.py -q  # 3 passed
.venv/bin/ruff check qcov/engine/reports.py qcov/i18n tests/engine/test_reports.py tests/i18n  # passed
.venv/bin/mypy qcov/engine/reports.py qcov/i18n  # passed
```
