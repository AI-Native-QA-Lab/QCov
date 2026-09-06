# Imported Reports Example

This project config discovers JUnit XML, coverage.py XML, Playwright JSON, and LCOV
without running tests.

```bash
qcov scan --config examples/imported-reports/qcov.yaml
qcov scan --config examples/imported-reports/qcov.yaml --format json
qcov gaps --config examples/imported-reports/qcov.yaml
```

Imported records are inventory observations, not obligation evidence. The final
command uses the explicit Refund evidence paths in this config. See
[中文版](README.zh-CN.md).
