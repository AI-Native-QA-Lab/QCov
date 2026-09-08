# 需求

## Core engine

产品接收版本化的 Obligation 与 Evidence 文件，进行校验，按义务计算四种状态（`COVERED`、`PARTIAL`、`MISSING`、`UNKNOWN`），并输出 JSON 或 Markdown。通过的证据必须精确匹配义务 ID、维度和所需类型。不计算聚合质量分数。`UNKNOWN` 不得伪装成通过。

## Delivered local capabilities

配置驱动的 `scan` 发现 pytest marker，并将 JUnit XML、coverage.py XML、Playwright JSON 与 LCOV 导入为 **inventory observation**。Iteration 4.5 提供 junit/playwright 的声明式 `EvidenceMapping`、`qcov map preview` 与 `--config` 评估合并。`qcov diff` 比较本地已提交版本上的显式义务与证据快照。`qcov policy check` 提供本地确定性门禁、精确且带时限的豁免，以及显式 `--as-of` 时间戳。

## Planned through Iteration 8

通过 4.5 后验证门槛之后，Iteration 5 可做映射加固（pytest marker 评估接线与有限 identity DX），以及仅提案性质的 AI：义务建议与变更风险分析。Iteration 6–7 分别只做 Quality Planner 与 Agentic Quality Loop。Iteration 8 在同一协议规则下接入生产证据生产者。AI 建议永不成为证据或门禁权威。见 [路线图](roadmap.md)。

## Still excluded without a new approved design

在无新的已批准设计前，Web UI、数据库持久化、远程 Git、外部插件加载、inventory 到义务的自动推断、策略 DSL、维度阈值、通配符或路径豁免，以及 coverage/LCOV 提升为可满足的 passed 证据仍不在范围内。Post-8 主题（QA for AI、Quality BOM、Adapter SDK、Continuous Quality Control Plane 打包）同样需要新设计。

## Pending requirement: broader mapping

有限尾缀 `*` identity 通配与 pytest marker 评估合并属于 Iteration 5。Coverage/LCOV
仍不得自动提升为可满足证据。未映射的通用导入仍仅为诊断与 inventory。
