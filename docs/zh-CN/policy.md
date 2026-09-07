# 策略门禁与豁免

`qcov policy check` 对既有覆盖计算执行本地、确定性的策略判断，不改变 obligation、evidence 或覆盖状态。

```bash
qcov policy check --config qcov.yaml --policy policy.yaml --as-of 2026-09-07T00:00:00+08:00
```

策略只允许 `rules.default.allowedStatuses` 中的状态。精确义务 ID 的有效豁免会产生 `WARN`；不允许的状态产生 `BLOCK` 和 `QCOV-POLICY-001`；到期豁免不生效，并在导致违规时产生 `QCOV-POLICY-002`。`--as-of` 必须带时区，保证结果可复现。

退出码：`0` 表示只有 PASS/WARN，`2` 表示存在 BLOCK，`4` 表示策略或输入无效。JSON 使用稳定英文键；Markdown 可用 `--locale zh-CN` 切换。
