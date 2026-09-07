# 路线图

Iteration 0 验证 Obligation → Evidence → Gap；Iteration 1 扩展 CLI 导入；Iteration 2 增加跨语言/工具适配器；Iteration 3 实现 PR Delta；Iteration 4 增加策略与豁免；Iteration 5–7 引入 AI 建议和规划；Iteration 8 接入生产证据。扩大范围前先验证接入时间、可解释性、缺口价值和 AI 建议接受率。

Iteration 1 现为本地首次价值里程碑：配置、pytest marker detection、JUnit XML 与 coverage.py XML inventory。

Iteration 2 通过明确的 built-in registry 增加本地 Playwright JSON 与 LCOV inventory reader；external adapter plugin 仍不在范围内。

Iteration 4 已提供独立的 `qcov policy check`：默认状态规则、带时区且可审计的精确豁免、显式 `--as-of` 与 PASS/WARN/BLOCK 门禁均保持本地确定性。
