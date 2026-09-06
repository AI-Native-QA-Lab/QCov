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

可用 `qcov scan --config examples/imported-reports/qcov.yaml` 验证本地发现。该示例还覆盖 Playwright JSON 和 LCOV inventory reader；两者都不会执行项目代码或创建 Quality Evidence。每项行为变更都必须保留 RED 测试及其 GREEN 结果记录。

运行 `python examples/pr-delta/demo.py` 可查看自包含的两个提交 `qcov diff`
示例；它只会创建并删除临时仓库。
