# Policy gates and waivers

`qcov policy check` evaluates local deterministic policy without changing coverage facts.

```bash
qcov policy check --config qcov.yaml --policy policy.yaml --as-of 2026-09-07T00:00:00+08:00
```

The Chinese [policy reference](../zh-CN/policy.md) is canonical. `0` means PASS/WARN only, `2` means BLOCK, and `4` means invalid input. `QCOV-POLICY-001` identifies an unwaived violation; `QCOV-POLICY-002` identifies an expired waiver that no longer permits one.
