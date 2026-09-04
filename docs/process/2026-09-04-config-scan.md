# Iteration 1 Config-Driven Scan Record

## Scope

Task 4 aggregates local pytest-marker detection, JUnit XML inventory, and
coverage.py XML inventory through `qcov scan --config`. It supports Markdown
and stable English-keyed JSON without executing project tests.

## TDD evidence

The CLI JSON test first failed with exit code 2 because `scan` had no
`--config`/`--format` options. After the discovery service and renderers were
implemented, 2026-09-04 checks passed:

```text
.venv/bin/python -m pytest tests/engine/test_scan.py tests/cli/test_commands.py -q  # 7 passed
.venv/bin/ruff check qcov/engine qcov/cli tests/engine tests/cli                    # passed
.venv/bin/mypy qcov/engine qcov/cli                                                  # passed
git diff --check                                                                      # passed
```

Missing configured report files remain `QCOV-SCAN-001` diagnostics; invalid
config remains a nonzero `QCOV-CONFIG-001` CLI failure.
