# 路线图

QCov 仍是本地、确定性的质量证据缺口引擎：报告某项义务还有什么未被证明。它不是行覆盖率检测器，也不是测试执行器。

## Delivered through Iteration 7

Iteration 0 验证 Obligation → Evidence → Gap。Iteration 1 增加配置驱动的 pytest marker、JUnit XML 与 coverage.py XML inventory 本地发现。Iteration 2 通过明确的 built-in registry 增加 Playwright JSON 与 LCOV inventory reader；external adapter plugin 仍不在范围内。Iteration 3 通过 `qcov diff` 提供只读的已提交树比较。Iteration 4 提供本地 `qcov policy check`：默认状态规则、可审计的精确豁免、显式 `--as-of` 与 PASS/WARN/BLOCK 判定。Iteration 4.5 提供声明式 `EvidenceMapping`（junit/playwright）、`qcov map preview`，以及 `--config` 评估合并。Iteration 5 增加 pytest marker 评估合并、有限 identity 后缀通配，以及仅提案 AI（`obligation suggest` / `risk analyze`，默认 offline provider）。Iteration 6 增加确定性 `qcov plan`：对未满足缺口按固定收益/成本启发式排序，产出 draft `QualityProposal`（`type: quality_plan`），指示下一步最值得验证什么——仍不是证据或门禁权威。Iteration 7 增加 Agentic Quality Loop 助手：必做 `qcov explain` 与 `qcov agent next`（稳定 `qcov.agent/v1` JSON），以及可选的 `qcov agent validate-evidence`（仅加载检查）。QCov 仍不执行测试、不写权威证据。见 [Agent 使用说明](agent.md)。

远程 Git、源码行级影响推断、策略 DSL、维度阈值、通配符豁免、coverage/LCOV 提升为 passed 证据，以及 inventory 自动推断在无后续设计批准前仍延后。

## Gate after 4.5

在加速 AI 之前，先用真实项目验证接入时间、可解释性与相对普通报告的缺口价值。映射必须保持声明式与本地。适配器仍不得推断「通过的测试」或「覆盖率」足以证明业务义务。设计见：
`docs/superpowers/specs/2026-09-08-post-4.5-iteration-roadmap-design.md`。说明见 [显式证据映射](mapping.md)。

## Planned Iteration 8

原则：AI 提出建议；策略批准；确定性引擎核验。AI 不得成为证据或门禁权威。

| 迭代 | 焦点 |
| --- | --- |
| **8** | 仅生产证据（runtime / incident / observability 类生产者，仍受协议规则约束） |

**Roadmap Complete through Iteration 8** 表示这条核心弧（缺口 → 变更 → 策略 → 映射 → AI 建议/规划/Agent 反馈 → 生产回流）收官。这是里程碑，不是产品终点。

## Post-8 backlog

以下方向需单独批准设计后再做：QA for AI 维度、Quality BOM、Adapter SDK / 更广生态、远程 Git 与更深 CI 自动化、策略 DSL 与维度阈值、coverage/LCOV 提升为可满足证据、inventory 自动推断义务、Web UI、持久化，以及打包的 Continuous Quality Control Plane。

## Validation gates before expansion

扩大到 AI 或生产适配器之前，先验证这些假设：Testing Obligation 比「需求—测试」追溯更有价值；初始接入足够快；缺口可解释；工具能发现普通报告掩盖的证据遗漏；AI 建议永不覆盖确定性判定。
