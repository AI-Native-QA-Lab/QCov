# Imported Reports Example

Imported records are inventory observations, not obligation evidence, until an
explicit `EvidenceMapping` binds selected **junit** or **playwright** identities.
coverage.py and LCOV stay inventory-only. This example includes
`mappings/refund.yaml` so `qcov map preview` and `qcov gaps --config` can show
mapped evidence alongside hand-authored Refund evidence.

```bash
qcov scan --config examples/imported-reports/qcov.yaml
qcov map preview --config examples/imported-reports/qcov.yaml --format json
qcov gaps --config examples/imported-reports/qcov.yaml
```

See [中文版](README.zh-CN.md) and [mapping docs](../../docs/en/mapping.md).
