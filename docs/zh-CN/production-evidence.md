# 生产证据

`ProductionObservationReport` 是 runtime、incident、observability 观察的本地 JSON/YAML inventory 格式。QCov 读取它时不会连接生产服务，也不会执行代码。

每条 observation 都有 id、类别、状态、带时区时间戳和可选字符串 attributes。通过 `scan.production` 配置文件。只有显式 `EvidenceMapping` 写出其 `production-observation` identity 后，观察才会成为证据；观察自身时间戳是该证据的执行时间，mapping 时间不能覆盖。

```bash
.venv/bin/python -m qcov scan --config examples/production-observations/qcov.yaml
.venv/bin/python -m qcov map preview --config examples/production-observations/qcov.yaml --format json
```

即使 observation 为 passed，没有 mapping 也不等于 `COVERED`；QCov 不会自动推断义务或维度。
