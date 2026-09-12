# Iteration 8：Production Evidence（纯）设计

## 目标

在不执行服务、不访问网络、也不改变 Gap / policy 权威的前提下，增加一个内置的本地生产观测 inventory producer。
它读取版本化 JSON 或 YAML 工件，将 runtime、incident、observability 观察保留为 `InventoryRecord`；只有经 `EvidenceMapping` 明确指向义务和维度的记录，才会被物化为 `QualityEvidence`。

原则不变：生产观察不是覆盖结论；AI 不是证据或门禁权威。

## 决策

采用一个严格的、QCov 自有的离线工件格式 `ProductionObservationReport`，由适配器名 `production-observation` 读取。

不直接绑定 OpenTelemetry、Sentry 或任一云平台：它们的导出格式和字段语义各异，直接接入会扩大本迭代的生态与网络范围。上游导出程序可在 QCov 外部把数据归一化为本格式。

## 协议

```yaml
apiVersion: qcov.dev/v1alpha1
kind: ProductionObservationReport
metadata:
  id: production-release-2026-09-11
observations:
  - id: checkout-runtime-slo
    category: runtime # runtime | incident | observability
    status: passed    # passed | failed | skipped | unknown
    timestamp: 2026-09-11T00:00:00+08:00
    attributes:
      service: checkout
      signal: availability
```

- `metadata.id` 与 `observations[].id` 非空；同一报告内 observation id 唯一。
- `timestamp` 必须带时区；`attributes` 是 string 到 string 的扁平字典。
- 解析或 schema 错误沿用 `QCOV-SCAN-001`，并且不产生部分记录。
- 每条记录的 inventory identity 是 `metadata.id::observation.id`，producer 是 `production-observation`，状态原样保留，metadata 含 category、timestamp 和 attributes。

## 配置与映射

`QCovConfig.scan.production` 是本地路径或 glob 列表；解析、缺失工件诊断、排序和去重完全沿用其他 scan 输入。

`MappingSource.producer` 扩展为 `junit | playwright | production-observation`。映射引擎将 production-observation 的 `passed`、`failed`、`skipped`、`unknown` 直接译为同名 `QualityEvidence.execution.status`；未知状态生成 `QCOV-MAP-003` 和 `unknown` 证据。production-observation 的 `observations[].timestamp` 是物化后 `QualityEvidence.execution.timestamp` 的唯一权威，mapping 的 `timestamp` / `defaultTimestamp` 不得覆盖它。没有 mapping 的记录始终只是 inventory。

不增加自动义务推断、类别到维度的推断、路径豁免、阈值、远程拉取或新的 CLI 命令。`qcov scan`、`qcov map preview` 和 `--config` 既有评估路径自然消费该生产者。

## 架构

```text
本地 ProductionObservationReport
  -> ProductionObservationAdapter.scan
  -> InventoryRecord(production-observation)
  -> 显式 EvidenceMapping
  -> QualityEvidence
  -> 既有 Gap Engine / policy check
```

任何一段缺失时，生产记录都不能使义务成为 `COVERED`。

## 错误与确定性

- 读取/解析/模型验证失败：一个 `QCOV-SCAN-001`，无 records。
- 重复 observation id：模型拒绝，适配器返回同一诊断。
- `scan_project` 的 adapter 汇总按名字排序；registry 顺序固定，测试锁定名称集合。
- `stable_evidence_id` 继续使用 producer 和 identity，故 production 映射得到稳定且不与测试 producer 混淆的 id。

## 测试与验收

TDD 下新增：

1. model：合法报告、无时区时间戳、重复 observation id 被拒绝；
2. adapter：runtime / incident / observability 记录、无效工件诊断；
3. scan / config：`scan.production` 解析与 registry / 汇总记录；
4. mapping：明确映射的 passed 记录能产生 evidence，failed 保持 failed，未映射记录不产生 evidence；
5. CLI：config 路径的 `scan` 与 `map preview` 显示生产记录，但未映射记录不改变 gaps；
6. regression：既有 JUnit / Playwright 映射和 Gap / policy 语义不变。

交付时同步双语公开 docs、示例、中文过程记录；路线图将 Iteration 8 标为 QCov 1.0 前的生产观测基础，并把 Iteration 9 作为 QCov 1.0 起点。运行 `pytest`、`ruff check .`、`mypy qcov`、`python -m build`、`git diff --check`。

## 非目标与后续边界

本迭代不实现 QA for AI、Q-BOM、Adapter SDK、远程 Git、Web UI、持久化或 Continuous Quality Control Plane。Adapter SDK 是 Iteration 9 / QCov 1.0 的单独设计项；其余能力按 1.5、2.0 或 Future 的独立设计推进。
