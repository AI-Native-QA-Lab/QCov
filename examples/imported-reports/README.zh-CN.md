# 导入报告示例

该项目配置发现 JUnit XML、coverage.py XML、Playwright JSON 和 LCOV，而不执行测试。
导入记录默认只是 inventory；本示例的 `mappings/refund.yaml` 用显式映射把 **junit /
playwright** 条目提升为可进入 Gap Engine 的证据。coverage.py 与 LCOV 仍仅为
inventory，不能映射为可满足证据。

```bash
qcov scan --config examples/imported-reports/qcov.yaml
qcov map preview --config examples/imported-reports/qcov.yaml --format json
qcov gaps --config examples/imported-reports/qcov.yaml
```

参见 [English](README.md) 与 [映射说明](../../docs/zh-CN/mapping.md)。
