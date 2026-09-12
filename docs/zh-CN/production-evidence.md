# 生产证据

`ProductionObservationReport` 是用于运行时、事故和可观测性观察的本地 JSON/YAML inventory
格式。QCov 读取它时绝不连接生产服务，也不执行代码。

每条观察包含 id、类别、状态、带时区时间戳以及可选字符串属性。通过 `scan.production`
配置文件。观察在显式 `EvidenceMapping` 指定其 `production-observation` identity 前始终只是
inventory。其观察时间戳会成为映射证据的执行时间戳，mapping 时间戳不能替代它。

```bash
.venv/bin/python -m qcov scan --config examples/production-observations/qcov.yaml
.venv/bin/python -m qcov map preview --config examples/production-observations/qcov.yaml --format json
```

通过的观察在没有该 mapping 时也不是 `COVERED`；QCov 不会从观察自动推断 obligation 或维度。
