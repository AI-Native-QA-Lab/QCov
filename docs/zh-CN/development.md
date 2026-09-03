# 开发

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/mypy qcov
.venv/bin/python -m build
```

先写 pytest，再写生产代码。Adapter 收集过程不得执行用户测试或产生副作用。
