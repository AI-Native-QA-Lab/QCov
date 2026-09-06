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
The example also exercises Playwright JSON and LCOV inventory readers; neither
reader executes project code or creates Quality Evidence.
Every behavior change must preserve a recorded RED test before its GREEN result.

Run `python examples/pr-delta/demo.py` for a self-contained two-commit
`qcov diff` example. It creates and removes a temporary repository only.
