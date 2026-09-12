# 需求

## Core engine

产品接收版本化的 Obligation 与 Evidence 文件，进行校验，按义务计算四种状态（`COVERED`、`PARTIAL`、`MISSING`、`UNKNOWN`），并输出 JSON 或 Markdown。通过的证据必须精确匹配义务 ID、维度和所需类型。不计算聚合质量分数。`UNKNOWN` 不得伪装成通过。

## Delivered local capabilities

配置驱动的 `scan` 发现 pytest marker，并将 JUnit XML、coverage.py XML、Playwright JSON 与 LCOV 导入为 **inventory observation**。Iteration 4.5 提供 junit/playwright 的声明式 `EvidenceMapping`、`qcov map preview` 与 `--config` 评估合并。`qcov diff` 比较本地已提交版本上的显式义务与证据快照。`qcov policy check` 提供本地确定性门禁、精确且带时限的豁免，以及显式 `--as-of` 时间戳。

## Delivered through Iteration 7（提案 + Agent 助手）

Iteration 5 完成映射加固（pytest marker 评估接线与有限 identity DX）以及仅提案
AI（`obligation suggest`、`risk analyze`）。Iteration 6 增加确定性 `qcov plan`
（对 unproven gaps 做固定收益/成本启发式，产出 `type: quality_plan` 的 draft
`QualityProposal`）。Iteration 7 增加 Agentic Quality Loop 助手：必做
`qcov explain` 与 `qcov agent next`（`contractVersion: qcov.agent/v1`），以及可选
`qcov agent validate-evidence`（仅加载检查）。提案与 Agent 助手永不成为证据或门禁权威。见 [Agent 使用说明](agent.md)。

Iteration 8 已交付本地 `production-observation` inventory producer；观察需经显式 mapping
才成为证据，并保留执行时间戳。见[生产证据](production-evidence.md)。

## 计划中的 Iteration 8 与 QCov 1.0 入口门槛

Iteration 8 在同一协议规则下接入离线 production-observation inventory producer。观察只有经显式 mapping 才能成为证据；AI/plan/Agent 助手永不成为证据或门禁权威。

Iteration 9 开启 QCov 1.0：真实项目验证、确定性的 Change → Obligation Impact、Adapter SDK v1 与协议稳定性。1.0 Release Gate 为至少 3 个真实项目（Python/pytest/coverage、Java/JUnit/JaCoCo、TypeScript/Playwright）、至少 30 条真实 obligation，并使首次价值时间不超过 10 分钟。见 [路线图](roadmap.md)。

## Still excluded without a new approved design

在无新的已批准设计前，Web UI、数据库持久化、远程 Git、inventory 到义务的自动推断、策略 DSL、维度阈值、通配符或路径豁免，以及 coverage/LCOV 提升为可满足的 passed 证据仍不在范围内。Adapter SDK v1 已列为 QCov 1.0 计划；更广生态/插件加载、QA for AI、Quality BOM 与 Continuous Quality Control Plane 打包仍需后续设计。

## Pending requirement: broader mapping

有限尾缀 `*` identity 通配与 pytest marker 评估合并属于 Iteration 5。Coverage/LCOV
仍不得自动提升为可满足证据。未映射的通用导入仍仅为诊断与 inventory。
