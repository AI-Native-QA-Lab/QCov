# CI Trigger and License Change Record

## Scope

The CI workflow now runs for every push as well as pull requests, so feature
branches receive the same `pytest`, Ruff, mypy, and package-build validation as
`main`. The repository license has changed from Apache-2.0 to PolyForm
Noncommercial License 1.0.0 using the official plain-text license document.

## Verification

2026-09-03 (Asia/Shanghai):

```text
workflow YAML check: push trigger present and pytest CI step present  # passed
.venv/bin/python -m pytest                                            # 20 passed
.venv/bin/ruff check .                                                 # passed
.venv/bin/mypy qcov                                                    # passed
.venv/bin/python -m build                                              # sdist and wheel built
git diff --check                                                       # passed
```

The official license source is
<https://polyformproject.org/licenses/noncommercial/1.0.0>.
