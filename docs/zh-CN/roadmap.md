# 路线图

QCov 仍是本地、确定性的质量证据缺口引擎：报告某项义务还有什么未被证明。它不是行覆盖率检测器，也不是测试执行器。

## Delivered through Iteration 4

Iteration 0 验证 Obligation → Evidence → Gap。Iteration 1 增加配置驱动的 pytest marker、JUnit XML 与 coverage.py XML inventory 本地发现。Iteration 2 通过明确的 built-in registry 增加 Playwright JSON 与 LCOV inventory reader；external adapter plugin 仍不在范围内。Iteration 3 通过 `qcov diff` 提供只读的已提交树比较。Iteration 4 提供本地 `qcov policy check`：默认状态规则、可审计的精确豁免、显式 `--as-of` 与 PASS/WARN/BLOCK 判定。

远程 Git、源码行级影响推断、策略 DSL、维度阈值、通配符豁免，以及 inventory 到证据的自动推断仍延后。

## Next: Iteration 4.5 mapping and validation

在进入 AI 工作前，先补上 ADR 0003 延后的首次价值闭环：**显式义务映射**（将 inventory observation 及相关 adapter 输出映射为 `QualityEvidence`），并用真实项目验证接入时间、可解释性，以及相对普通报告的缺口价值。

映射必须保持声明式与本地。适配器仍不得推断「通过的测试」或「覆盖率」足以证明业务义务。

## Later iterations

Iteration 5–7 仅可将 AI 作为确定性策略门禁之下的建议与规划层；AI 不得成为证据或门禁权威。Iteration 8 接入生产证据。

## Validation gates before expansion

扩大到 AI 或生产适配器之前，先验证这些假设：Testing Obligation 比「需求—测试」追溯更有价值；初始接入足够快；缺口可解释；工具能发现普通报告掩盖的证据遗漏；AI 建议永不覆盖确定性判定。
