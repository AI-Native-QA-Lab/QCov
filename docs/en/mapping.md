# Explicit evidence mapping

`EvidenceMapping` files declare exact inventory identities that become
`QualityEvidence`. Mapping is declarative: QCov never infers an obligation from
a test name or coverage rate.

```bash
qcov map preview --config examples/imported-reports/qcov.yaml --format json
qcov gaps --config examples/imported-reports/qcov.yaml
```

## Configuration

Add `mapping:` path/glob entries to `qcov.yaml`. Iteration 4.5 allows only
`from.producer: junit` or `playwright`. When `mapping:` is configured,
`evidence:` may be empty. coverage.py and LCOV remain inventory-only and cannot
be mapped to covering evidence.

## Commands

- `qcov map preview --config …` previews mapped evidence and `QCOV-MAP-*`
  diagnostics without writing files.
- `gaps` / `check` / `report` / `policy check` with `--config` merge authored
  evidence and mapped evidence; JSON includes `mappingDiagnostics`.

## Diagnostic codes

| Code | Meaning |
| --- | --- |
| `QCOV-MAP-001` | inventory identity not found |
| `QCOV-MAP-002` | evidence id conflict (fatal, exit 4) |
| `QCOV-MAP-003` | unrecognized inventory status; materialized as `unknown` |
| `QCOV-MAP-005` | multiple inventory records match the same identity |
| `QCOV-MAP-006` | artifact path could not be relativized to the config directory |
| `QCOV-MAP-007` | duplicate EvidenceMapping `metadata.id` (fatal, exit 4) |

Mapping is a declaration, not an inference.
