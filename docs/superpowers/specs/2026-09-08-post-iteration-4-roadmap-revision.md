# Iteration 4 后路线图修订

## 背景

Iteration 0–4 已按原 Deferred Roadmap 落地：Gap Engine、inventory 导入、
内置适配器 registry、本地 `qcov diff`、本地 `qcov policy check`。对照
`2026-09-02` MVP 设计后的偏差主要是：

1. Iteration 2 有意收窄：无外部插件 / SDK，仅 built-in registry。
2. 通用导入保持 inventory-only（ADR 0003），显式映射层尚未实现。
3. 公开需求与 `AGENTS.md` 仍把已交付的 Git delta / policy 写成 MVP 排除项。
4. 中文路线图缺少 Iteration 3 完成说明。

产品主线未跑偏：本地、确定性、无聚合分数、AI 未进入证据或门禁权威。

## 决策

1. **文档对齐现状**：更新双语 `roadmap` / `requirements` 与 `AGENTS.md`，
   区分「已交付」「仍排除」「待补映射」。
2. **插入 Iteration 4.5**：在 AI（5–7）之前优先显式义务映射与真实接入验证。
3. **对外表述**：继续定位为质量证据缺口引擎，避免「代码测试覆盖检测」。
4. **不回退** Iteration 3 / 4；远程 Git、行级影响、策略 DSL、通配符豁免、
   inventory 自动推断仍需独立设计批准。

## 非目标

本次修订只改文档与贡献者规则，不改协议、CLI 或引擎行为。
