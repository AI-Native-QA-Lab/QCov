# QCov

> **发现你的测试尚未证明什么。**

[English](README.md) · [核心概念](docs/zh-CN/concepts.md) · [路线图](docs/zh-CN/roadmap.md) · [贡献指南](CONTRIBUTING.zh-CN.md)

QCov 是面向 AI Native 软件交付的开源**质量证据缺口引擎**与**质量覆盖协议**。它不替代 pytest、JUnit、Playwright、覆盖率工具、安全扫描或可观测性平台，而是判断这些工具的证据是否足以证明某项需求、风险或变更。

## MVP

本地确定性 MVP 校验 Testing Obligation 与 Quality Evidence，并输出
`COVERED`、`PARTIAL`、`MISSING` 或 `UNKNOWN`。AI、数据库、仪表盘、Git Delta 和策略门禁均不在当前范围内。

```bash
.venv/bin/python -m qcov gaps \
  --obligation examples/refund/obligation.yaml \
  --evidence examples/refund/evidence \
  --locale zh-CN
```

Refund 示例会报告 `PARTIAL`：已有行为、边界和数据证据；并发、幂等性和生产证据仍缺失。

要发现现有本地报告而不执行测试，请运行
`qcov scan --config examples/imported-reports/qcov.yaml`；加入 `--format json`
可输出机器可读的 inventory 信息。参见[导入报告示例](examples/imported-reports/README.zh-CN.md)。

## 项目入口

- [需求](docs/zh-CN/requirements.md)
- [架构](docs/zh-CN/architecture.md)
- [协议](docs/zh-CN/protocol.md)
- [技术设计](docs/zh-CN/technical-design.md)
- [开发指南](docs/zh-CN/development.md)
- [过程记录](docs/zh-CN/process.md)

## 许可证

[PolyForm Noncommercial License 1.0.0](LICENSE)。
