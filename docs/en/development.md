# Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/mypy qcov
.venv/bin/python -m build
```

Use `pytest` before production code. Keep adapter collection side-effect free.

Try local discovery with `qcov scan --config examples/imported-reports/qcov.yaml`.
Every behavior change must preserve a recorded RED test before its GREEN result.
