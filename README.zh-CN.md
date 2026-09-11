# QCov

> **发现你的测试尚未证明什么。**

[English](README.md) · [核心概念](docs/zh-CN/concepts.md) · [Agent](docs/zh-CN/agent.md) · [路线图](docs/zh-CN/roadmap.md) · [贡献指南](CONTRIBUTING.zh-CN.md)

QCov 是开源**质量证据缺口引擎**与**质量覆盖协议**。它不替代 pytest、JUnit、
Playwright、覆盖率工具、安全扫描或可观测性平台，而是判断这些工具的证据是否足以
证明某项需求、风险或变更。

## 功能

- 确定性缺口评估：`COVERED`、`PARTIAL`、`MISSING`、`UNKNOWN`
- 本地 inventory 扫描：pytest marker、JUnit、coverage.py、Playwright（`scan.playwright`）、LCOV（`scan.lcov`）、生产观察（`scan.production`）
- 显式 `EvidenceMapping`：将 junit/playwright/production-observation inventory 提升为 `QualityEvidence`
- 本地 `qcov diff`：比较已提交 Git 树上的义务/证据快照
- 本地 `qcov policy check`：精确且带时限的豁免
- 仅提案助手：`qcov obligation suggest`、`qcov risk analyze`，以及确定性
  `qcov plan`（产出 draft `QualityProposal`；不是证据，也不是门禁权威）
- Markdown / JSON 报告，支持 `en` / `zh-CN` 展示

不在范围内：AI 门禁裁决、Web UI、数据库、远程 Git Host API、外部插件，以及把
coverage/LCOV 行覆盖率提升为可满足义务的证据。

## 安装

需要 Python 3.11+。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## 快速开始

```bash
.venv/bin/python -m qcov gaps \
  --obligation examples/refund/obligation.yaml \
  --evidence examples/refund/evidence \
  --locale zh-CN
```

Refund 示例会报告 `PARTIAL`：已有行为、边界和数据证据；并发、幂等性和生产证据仍缺失。

## 使用

```bash
# 发现本地报告 inventory（不执行测试）
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml

# 预览声明式 inventory → evidence 映射
.venv/bin/python -m qcov map preview \
  --config examples/imported-reports/qcov.yaml --format json

# 使用配置默认值与可选 mapping 评估缺口
.venv/bin/python -m qcov gaps --config examples/imported-reports/qcov.yaml

# 比较已提交的义务/证据快照
.venv/bin/python -m qcov diff --base origin/main --head HEAD --config qcov.yaml

# 本地策略门禁
.venv/bin/python -m qcov policy check \
  --config qcov.yaml --policy policy.yaml \
  --as-of 2026-09-07T00:00:00+08:00

# 义务 / 变更风险草案（默认 offline；不是证据）
.venv/bin/python -m qcov obligation suggest \
  --config qcov.yaml --requirements requirements.md --format json
.venv/bin/python -m qcov risk analyze \
  --config qcov.yaml --base HEAD~1 --head HEAD --format json
```

参见[导入报告示例](examples/imported-reports/README.zh-CN.md)、
[显式证据映射](docs/zh-CN/mapping.md)、[PR 质量覆盖增量](docs/zh-CN/pr-delta.md)
与[策略门禁与豁免](docs/zh-CN/policy.md)，以及[生产证据](docs/zh-CN/production-evidence.md)。

## 文档

- [需求](docs/zh-CN/requirements.md)
- [架构](docs/zh-CN/architecture.md)
- [协议](docs/zh-CN/protocol.md)
- [技术设计](docs/zh-CN/technical-design.md)
- [开发指南](docs/zh-CN/development.md)
- [显式证据映射](docs/zh-CN/mapping.md)
- [PR 质量覆盖增量](docs/zh-CN/pr-delta.md)
- [过程记录](docs/zh-CN/process.md)

## 贡献

请阅读 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md) 与 [AGENTS.md](AGENTS.md)。
采用测试先行，完成前运行 `pytest`、`ruff check .`、`mypy qcov`、
`python -m build` 与 `git diff --check`。

## 许可证

[PolyForm Noncommercial License 1.0.0](LICENSE)。
