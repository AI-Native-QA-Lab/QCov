# 导入报告示例

该项目配置发现 JUnit XML 和 coverage.py XML，而不执行测试：

```bash
qcov scan --config examples/imported-reports/qcov.yaml
qcov scan --config examples/imported-reports/qcov.yaml --format json
qcov gaps --config examples/imported-reports/qcov.yaml
```

导入记录只是 inventory observation，不会自动成为 Obligation 证据；最后一条命令使用配置中明确指定的 Refund Evidence 路径。See [English](README.md)。
