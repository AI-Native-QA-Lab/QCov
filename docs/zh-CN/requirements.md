# 需求

## Core engine

产品接收版本化的 Obligation 与 Evidence 文件，进行校验，按义务计算四种状态（`COVERED`、`PARTIAL`、`MISSING`、`UNKNOWN`），并输出 JSON 或 Markdown。通过的证据必须精确匹配义务 ID、维度和所需类型。不计算聚合质量分数。`UNKNOWN` 不得伪装成通过。

## Delivered local capabilities

配置驱动的 `scan` 发现 pytest marker，并将 JUnit XML、coverage.py XML、Playwright JSON 与 LCOV 导入为 **inventory observation**。Iteration 4.5 提供 junit/playwright 的声明式 `EvidenceMapping`、`qcov map preview` 与 `--config` 评估合并。`qcov diff` 比较本地已提交版本上的显式义务与证据快照。`qcov policy check` 提供本地确定性门禁、精确且带时限的豁免，以及显式 `--as-of` 时间戳。

## Still excluded without a new approved design

在无新的已批准设计前，AI 提供方、Web UI、数据库持久化、远程 Git、外部插件加载、inventory 到证据的自动推断、策略 DSL、维度阈值，以及通配符或路径豁免仍不在范围内。

## Pending requirement: broader mapping

通配符 identity、coverage/LCOV 提升为可满足证据，以及 pytest marker 进入评估路径仍属后续。未映射的通用导入仍仅为诊断与 inventory。
