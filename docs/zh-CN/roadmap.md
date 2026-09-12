# 路线图

QCov 是本地、确定性的质量证据缺口引擎，回答某项显式需求、风险或变更还有什么未被证明；它不是行覆盖率检测器，也不是测试执行器。

## 已交付至 Iteration 7

Iteration 0–4 建立显式 Obligation → Evidence → Gap 评估、本地 inventory 发现、已提交树 `qcov diff` 与确定性本地 `qcov policy check`。Iteration 4.5 增加声明式 `EvidenceMapping` 与 map preview。Iteration 5–7 增加仅提案助手、确定性规划与 `qcov.agent/v1` 助手。这些助手不执行测试、不写入权威证据，也不决定门禁。见 [Agent 使用说明](agent.md)。

## 计划中的 Iteration 8：生产观测基础

Iteration 8 在既有协议规则下增加离线 production-observation inventory producer。runtime、incident 与 observability 观察在经过显式 `EvidenceMapping` 物化为证据前始终只是 inventory。它为真实验证提供基础，不代表生产反馈或产品路线图已经完成。

## QCov 1.0 — Find the Gap

**核心问题：** What is still unproven?

**目标：** 在不依赖 AI 保证核心正确性的前提下，证明 QCov 能在真实项目中创造价值。

Iteration 9 是 1.0 的交付主线：

| 工作流 | 交付结果 |
| --- | --- |
| 真实项目验证 | 验证 Python/pytest/coverage、Java/JUnit/JaCoCo、TypeScript/Playwright；目标至少 3 个项目、30 条真实 obligation，首次价值时间不超过 10 分钟。 |
| Change → Obligation Impact | 以确定性 path/package/module/service/API/component mapping 输出受影响义务及缺口 delta，提供 `qcov impact`、`qcov affected` 与本地 `qcov diff`。 |
| 适配器可扩展性 | 定义 `qcov.adapter/v1` 与 Adapter SDK v1，但适配器不是证据权威。JUnit PASS 或覆盖率仍不能直接证明业务义务。 |
| 协议稳定性 | 将 `qcov.dev/v1`、`qcov.agent/v1`、`qcov.impact/v1`、`qcov.adapter/v1` 固化为兼容性承诺。 |

1.0 Release Gate 必须证明普通测试、覆盖率和静态报告不能直接暴露的价值：发现关键或此前未知、可解释的质量缺口；并记录 false-gap rate、Gap → Added Verification conversion 与开发/QA 接受度。

## QCov 1.5 — Understand & Plan

**核心问题：** What should we verify next?

**目标：** AI-assisted Quality Evidence Intelligence。

在 1.0 验证后，增加 AI Obligation Discovery、AI 建议的 Change Impact、`qcov explain --ai`、与确定性 `qcov plan` 并存的 AI Suggested Plan，以及 Quality Evidence ROI。AI 提案必须与权威 obligation 和确定性 impact 分离。AI 可以理解、建议、解释、规划；不能证明证据或决定门禁。

## QCov 2.0 — Close the Loop

**核心问题：** How can agents continuously close quality gaps?

**目标：** AI Native Quality Planning。

将 Agent 契约从 `qcov.agent/v1` 演进为另行设计的 `qcov.agent/v2`，接收 candidate evidence；确定性系统仍须 Validate、Normalize、Map、Evaluate。Agent 不能把自己的工作标记为 `COVERED`。该阶段也将设计 QA for AI 证据维度、生产质量反馈闭环与 Quality BOM。

## Future：Continuous Quality Control Plane

仅在 2.0 之后探索：跨项目质量图、组织策略、历史证据、Release Intelligence、跨仓库影响、多 Agent 协作与合规证据。Web UI、持久化、远程 Git、inventory 到 obligation 的自动推断、策略 DSL、维度阈值、通配符/路径豁免以及 coverage/LCOV 提升为可满足证据，仍需单独批准设计。
