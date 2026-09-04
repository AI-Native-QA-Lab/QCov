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

可用 `qcov scan --config examples/imported-reports/qcov.yaml` 验证本地发现。每项行为变更都必须保留 RED 测试及其 GREEN 结果记录。
