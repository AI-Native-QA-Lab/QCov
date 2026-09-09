# 核心概念

QCov 的 **Testing Obligation** 描述为何必须验证某项需求、风险、不变量或变更；**Quality Evidence** 是映射到义务的机器可读证明。引擎比较所需与已观测证据，输出可解释的缺口，而非质量百分比。

**QualityProposal** 是 `qcov obligation suggest` / `qcov risk analyze` / `qcov plan` 产出的草案建议。`qcov plan` 对未满足缺口应用确定性启发式，产出 `quality_plan` 草案。提案不是证据，也不会改变 `policy check` 或 Gap Engine 判定：AI 提出建议；策略批准；确定性引擎核验。
