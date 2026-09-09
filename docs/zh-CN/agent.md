# Agent 使用说明

QCov **不**执行测试，也**不**写入权威证据。Coding agent 通过本地 CLI 助手选择下一步验证、解释缺口，并可选择检查证据 YAML 能否加载。门禁仍是 `qcov gaps` / `qcov policy check`。

## 建议闭环

```text
qcov gaps / qcov plan
→ qcov agent next --format json
→ （外部）执行测试并编写 QualityEvidence YAML
→ qcov explain …（可选排障）
→ qcov agent validate-evidence …（可选加载检查；不是 COVERED / 不是 PASS）
→ qcov gaps / qcov policy check
```

## 命令

| 命令 | 作用 |
| --- | --- |
| `qcov explain` | 确定性解释 gap、plan item，或证据为何未满足（`--mode gap` 或 `evidence`） |
| `qcov agent next` | 从 `--plan` 或现场评估（`--config` / 义务+证据）给出 top-N 下一步 |
| `qcov agent validate-evidence` | 仅协议加载检查（`validForLoad`）；绝不表示 COVERED 或 policy PASS |

这些命令的 JSON 输出使用稳定外壳：

```json
{
  "contractVersion": "qcov.agent/v1",
  "command": "explain",
  "payload": {}
}
```

默认 `--format` 为 markdown；机器契约用 `--format json`。既有 `gaps` / `plan` JSON **不**包此外壳。

## 边界

- explain / next 永不满足 gap，也不改写 policy 判定。
- Proposal（含 `quality_plan`）永不当证据。
- Agent 不得伪造证据或绕过 hard gate。
