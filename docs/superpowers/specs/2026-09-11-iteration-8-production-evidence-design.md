# Iteration 8：Production Evidence（纯）设计

## 目标与边界

增加本地、确定性的 `production-observation` inventory producer。它读取版本化 JSON/YAML 工件，保留 runtime、incident、observability 观察；只有显式 `EvidenceMapping` 才会物化为 `QualityEvidence`。不执行服务、不联网、不自动推断义务或维度，也不改变 Gap / policy 权威。

## 协议与映射

`ProductionObservationReport` 使用 `apiVersion: qcov.dev/v1alpha1`，含非空 `metadata.id` 和 observations。每条 observation 含唯一非空 `id`、`category`（runtime|incident|observability）、`status`（passed|failed|skipped|unknown）、带时区 `timestamp` 与 string-to-string `attributes`。记录 identity 为 `report-id::observation-id`，producer 为 `production-observation`。

`QCovConfig.scan.production` 接受本地路径/glob。`EvidenceMapping.from.producer` 扩展为 `production-observation`。映射时状态原样传入 execution；production observation 的 timestamp 是证据 execution timestamp 的唯一权威，mapping 时间不得覆盖。无 mapping 的记录不能使义务 COVERED。

## 验收

模型、adapter、config/scan、mapping、CLI 和 docs 均以 RED→GREEN 测试覆盖；同步双语公开文档、中文过程记录与路线图。最终执行 pytest、ruff、mypy、build、diff check。
