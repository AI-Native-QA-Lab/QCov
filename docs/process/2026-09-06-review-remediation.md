# Review Remediation Record

## Scope

This record closes the implementation findings from the 2026-09-06 review of
the Iteration 0 and Iteration 1 QCov code paths.

## RED evidence

Focused tests were added at the public engine, report, scan, and CLI seams.
Before implementation, the focused run reported eight failures:

```text
.venv/bin/pytest tests/engine/test_gaps.py tests/engine/test_reports.py tests/engine/test_scan.py tests/cli/test_commands.py -q
# 8 failed, 13 passed
```

The failures demonstrated absent evidence being reported as `MISSING`, invalid
output from `qcov init`, partial `--config` overrides being ignored, absent
observed evidence in Markdown, no pytest file/count scan facts, and no
`--obligations` compatibility alias.

An additional full-flow check exposed hidden `.venv` dependency tests in the
pytest scan file list. A focused adapter test failed before the scanner was
restricted to visible project paths.

## GREEN implementation

- Absent evidence for an obligation is `UNKNOWN`; evidence for that obligation
  but not its required dimension remains `MISSING`.
- `init` emits a valid v1alpha1 `QCovConfig`.
- Explicit obligation and evidence arguments override their own configured
  defaults independently.
- Markdown reports list observed evidence IDs; pytest scan summaries list test
  files and marker record counts.
- Shared path resolution preserves the diagnostic behavior for absent scan
  artifacts, and inventory scanning has its own protocol.
- Pytest discovery excludes hidden dependency directories such as `.venv`.

## GREEN verification

```text
.venv/bin/pytest tests/engine/test_gaps.py tests/engine/test_reports.py tests/engine/test_scan.py tests/cli/test_commands.py -q
# 21 passed
.venv/bin/ruff check qcov tests
# passed
```

Final verification on 2026-09-06 (Asia/Shanghai) passed:

```text
.venv/bin/pytest -q
# 40 passed
.venv/bin/ruff check .
# passed
.venv/bin/mypy qcov
# 20 source files, no issues
.venv/bin/python -m qcov gaps --config examples/imported-reports/qcov.yaml --format json
# QO-REFUND-001 PARTIAL with observed evidence IDs
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml --format json
# 3 adapters; JUnit 2 records, coverage.py 1 record, no diagnostics
.venv/bin/python -m build
# qcov-0.1.0a0.tar.gz and qcov-0.1.0a0-py3-none-any.whl built
git diff --check
# passed
```
