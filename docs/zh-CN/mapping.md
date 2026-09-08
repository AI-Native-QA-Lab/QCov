# 显式证据映射

`EvidenceMapping` 用声明式规则，把 inventory 中的精确 `identity` 提升为
`QualityEvidence`。QCov **不会**根据测试名或覆盖率推断义务。

```bash
qcov map preview --config examples/imported-reports/qcov.yaml --format json
qcov gaps --config examples/imported-reports/qcov.yaml
```

## 配置

在 `qcov.yaml` 中增加 `mapping:` 路径/glob。本迭代仅允许 `from.producer` 为
`junit` 或 `playwright`。配置了 `mapping:` 时，`evidence:` 可以为空。
coverage.py 与 LCOV 仍仅为 inventory，不能映射为可满足义务的证据。

## 命令

- `qcov map preview --config …`：只读预览将生成的证据与 `QCOV-MAP-*` 诊断。
- `gaps` / `check` / `report` / `policy check` 在使用 `--config` 且含 mapping
  时，合并手写证据与映射产物；JSON 增加 `mappingDiagnostics`。

## 诊断码

| 码 | 含义 |
| --- | --- |
| `QCOV-MAP-001` | inventory 中无匹配 identity |
| `QCOV-MAP-002` | evidence id 冲突（致命，退出码 4） |
| `QCOV-MAP-003` | 未识别的 inventory status，按 `unknown` 物化 |
| `QCOV-MAP-005` | 多个 inventory 记录匹配同一 identity |
| `QCOV-MAP-006` | artifact 无法相对化到配置目录 |
| `QCOV-MAP-007` | EvidenceMapping `metadata.id` 重复（致命，退出码 4） |

映射是声明，不是推断。
