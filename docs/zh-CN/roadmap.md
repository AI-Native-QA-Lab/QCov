# 路线图

QCov 是本地、确定性的质量证据缺口引擎，回答某项显式需求、风险或变更还有什么未被证明；它不是行覆盖率检测器，也不是测试执行器。

## 已交付至 Iteration 8

Iteration 0–4 建立 Obligation → Evidence → Gap 评估、本地 inventory 发现、已提交树 `qcov diff` 与确定性本地 `qcov policy check`。Iteration 4.5 增加声明式 `EvidenceMapping` 与 map preview。Iteration 5–7 增加仅提案助手、确定性规划与 `qcov.agent/v1` 助手；它们不执行测试、不写入权威证据，也不决定门禁。Iteration 8 增加本地 `production-observation` inventory producer：runtime、incident 与 observability 观察只有经显式 mapping 才会成为证据。见 [Agent 使用说明](agent.md) 与[生产证据](production-evidence.md)。

## QCov 1.0 — Find the Gap

**核心问题：** What is still unproven?

**目标：** 在不依赖 AI 保证核心正确性的前提下，证明 QCov 能在真实项目中创造可度量的价值。

Iteration 9 是 1.0 的交付主线：

| 工作流 | 交付结果 |
| --- | --- |
| 真实项目验证 | 验证 `ai-native-qa-agents`（Python/pytest/coverage）、`ai4se-demo-project`（Java/JUnit/JaCoCo）与 `naodeng.com.cn`（TypeScript/Playwright）；以 `ai-test-auditor` 作为额外 TypeScript/Node 生态案例。目标至少 3 个项目、30 条真实 obligation，首次价值时间不超过 10 分钟。 |
| Change → Obligation Impact | 以确定性的仓库相对 path glob mapping 输出受影响义务；提供两个本地快照时，再通过 `qcov impact`、`qcov affected` 与 `qcov diff` 输出缺口 delta。更高层 package/module/service/API mapping 必须预先展开为路径。 |
| 适配器可扩展性 | 定义进程内 `qcov.adapter/v1` 契约并增加 JaCoCo XML inventory reader；适配器不是证据权威。JUnit PASS 或覆盖率仍不能直接证明业务义务，外部插件加载继续延后。 |
| 协议稳定性 | 保留已发布的 `qcov.dev/v1alpha1`，并将 `qcov.agent/v1`、`qcov.impact/v1`、`qcov.adapter/v1` 固化为兼容性承诺；不隐式改名核心协议。 |
| Documentation and onboarding（文档与上手） | 清理双语 README；提供经过验证的安装路径、首个可运行示例、命令与配置说明、故障排查，使 Python、Java 或 TypeScript 的新用户无需阅读源码即可获得首次价值。 |

1.0 Release Gate 要求 3 个真实项目、3 种技术栈、至少 30 条真实 Testing Obligation，且首次价值时间不超过 10 分钟；还须展示普通测试、覆盖率和静态报告不能直接暴露的关键或此前未知、可解释缺口，并记录 false-gap rate、Gap → Added Verification conversion 与开发/QA 接受度。

文档门槛要求双语 README 导航一致、安装与快速开始命令已验证、可链接到配置和示例、明确本地边界与证据权威边界，并提供故障排查路径。文档是 1.0 的产品交付，不是发布后的清理工作。

## QCov 1.5 — Understand & Plan

**核心问题：** What should we verify next?

**目标：** AI-assisted Quality Evidence Intelligence。

1.0 验证后，以下仅是 1.5 的候选主题，均需另行批准设计：AI Obligation Discovery、AI 建议的 Change Impact、`qcov explain --ai`、与确定性 `qcov plan` 并存的 AI Suggested Plan，以及 Quality Evidence ROI。任何 AI 提案都必须与权威 obligation 和确定性 impact 分离。AI 可以理解、建议、解释、规划；不能证明证据或决定门禁。

## QCov 2.0 — Close the Loop

**核心问题：** How can agents continuously close quality gaps?

**目标：** AI Native Quality Planning。

以下仅是 2.0 的候选主题，均需另行批准设计：将 Agent 契约从 `qcov.agent/v1` 演进为接收 candidate evidence 的 `qcov.agent/v2`，以及设计 QA for AI 证据维度、生产质量反馈闭环与 Quality BOM。若获批准，确定性系统仍须 Validate、Normalize、Map、Evaluate；Agent 不能把自己的工作标记为 `COVERED`。

## Future：Continuous Quality Control Plane

仅在 2.0 之后探索：跨项目质量图、组织策略、历史证据、Release Intelligence、跨仓库影响、多 Agent 协作与合规证据。Web UI、持久化、远程 Git、inventory 到 obligation 的自动推断、策略 DSL、维度阈值、通配符/路径豁免以及 coverage/LCOV 提升为可满足证据，仍需单独批准设计。
