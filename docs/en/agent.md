# Agent playbook

QCov does **not** run tests or write authoritative evidence. Coding agents use
local CLI helpers to choose the next verification step, explain gaps, and
optionally check that evidence YAML loads. Gates remain `qcov gaps` /
`qcov policy check`.

## Suggested loop

```text
qcov gaps / qcov plan
→ qcov agent next --format json
→ (external) run tests and author QualityEvidence YAML
→ qcov explain … (optional troubleshooting)
→ qcov agent validate-evidence … (optional load check; not COVERED / not PASS)
→ qcov gaps / qcov policy check
```

## Commands

| Command | Role |
| --- | --- |
| `qcov explain` | Deterministic reasons for a gap, plan item, or evidence mismatch |
| `qcov agent next` | Top-N next steps from `--plan` or live evaluation (`--config` / obligation+evidence) |
| `qcov agent validate-evidence` | Protocol load check only (`validForLoad`); never claims COVERED or policy PASS |

JSON outputs for these commands wrap a stable envelope:

```json
{
  "contractVersion": "qcov.agent/v1",
  "command": "explain",
  "payload": {}
}
```

Default `--format` is markdown; use `--format json` for the machine contract.
Existing `gaps` / `plan` JSON is unchanged (no agent envelope).

## Boundaries

- Explain and next never satisfy gaps or change policy decisions.
- Proposals (`quality_plan` and others) are never evidence.
- Agents must not forge evidence or bypass hard gates.
