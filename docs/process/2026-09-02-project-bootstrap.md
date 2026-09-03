# QCov Project Bootstrap Record

## Scope

Task 1 of `docs/superpowers/plans/2026-09-02-qcov-mvp.md` establishes the
package baseline, repository rules, CI, and the first architecture decision.

## Expected verification

- `pytest tests/test_package.py -q` verifies the package version.
- `ruff check .` checks style.
- `mypy qcov` checks package types.

Actual results will be appended after the task checks complete.

## Actual verification

2026-09-02 (Asia/Shanghai): the initial RED test was observed with
`pytest tests/test_package.py -q`; it failed because the `qcov` package did not
exist. The shell's `python` command was unavailable, so the project records
`python3` as the environment-compatible interpreter in `AGENTS.md`.

The first dependency installation exposed an ordering issue: package metadata
referenced the public README scheduled for the documentation task. The package
now uses an inline metadata synopsis until Task 8 writes the complete README.
This did not change the product scope or protocol.

After creating `.venv` and installing `.[dev]`, these checks passed:

```text
.venv/bin/python -m pytest tests/test_package.py -q  # 1 passed
.venv/bin/ruff check .                               # passed
.venv/bin/mypy qcov                                  # 4 source files, no issues
git diff --check                                     # passed
```
