# 协议

`qcov.dev/v1alpha1` 定义 `TestingObligation`、`QualityEvidence` 与 `QualityPolicy`。机器字段使用英文；多语言内容使用 `en` 和 `zh-CN`。公开 Schema 位于 `schemas/`，错误码如 `QCOV-SCHEMA-001` 不翻译。

`QCovConfig` 同样使用 `qcov.dev/v1alpha1`；无效配置返回 `QCOV-CONFIG-001`，非致命的报告读取问题使用 `QCOV-SCAN-001`。

QCov 1.0 新增兼容性的 `qcov.impact/v1` 与 `qcov.adapter/v1` 契约。Impact 输出 Schema 为 [qcov.impact-v1.schema.json](../../schemas/qcov.impact-v1.schema.json)；其中 `changedFiles`、义务 ID、Gap 数组、diagnostics 及排序规则在 1.0 中保持稳定。`qcov.agent/v1` 仍是提案/助手输出并保持既有兼容契约。这些契约不会重命名或削弱 `qcov.dev/v1alpha1`，1.0 不引入 `qcov.agent/v2`。
