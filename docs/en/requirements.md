# Requirements

## Core engine

The product accepts versioned obligation and evidence files, validates them,
computes four states per obligation (`COVERED`, `PARTIAL`, `MISSING`,
`UNKNOWN`), and renders JSON or Markdown. Exact passed evidence must match
obligation ID, dimension, and required type. No aggregate quality score is
calculated. `UNKNOWN` must never masquerade as a pass.

## Delivered local capabilities

Config-driven `scan` discovers pytest markers and imports JUnit XML,
coverage.py XML, Playwright JSON, LCOV, and local `ProductionObservationReport`
artifacts as **inventory observations** until
an explicit obligation mapping exists. Iteration 4.5 provides declarative
`EvidenceMapping` for junit/playwright identities, `qcov map preview`, and
`--config` evaluation merge. `qcov diff` compares explicit obligation and
evidence snapshots across local committed revisions. `qcov policy check`
applies local deterministic gates with exact, expiring waivers and an explicit
`--as-of` timestamp.

## Delivered through Iteration 8 (proposal + agent helpers + production evidence)

Iteration 5 adds mapping hardening (pytest-marker evaluation wiring and limited
identity DX) plus proposal-only AI (`obligation suggest`, `risk analyze`).
Iteration 6 adds deterministic `qcov plan` (fixed benefit/cost heuristics over
unproven gaps → draft `QualityProposal` with `type: quality_plan`). Iteration 7
adds Agentic Quality Loop helpers: required `qcov explain` and `qcov agent next`
(`contractVersion: qcov.agent/v1`), plus optional `qcov agent validate-evidence`
(load check only). Proposals and agent helpers never become evidence or gate
authority. See [agent playbook](agent.md). Iteration 8 adds local
`production-observation`; observations require explicit mapping and retain their
own execution timestamp. See [production evidence](production-evidence.md).

## QCov 1.0 entry gate

Iteration 9 begins QCov 1.0 with real-project validation, deterministic Change
→ Obligation Impact, Adapter SDK v1, protocol stability, and documentation /
onboarding readiness. The release gate is at least three real projects across
Python/pytest/coverage, Java/JUnit/JaCoCo, and TypeScript/Playwright (the fixed
required cases are `ai-native-qa-agents`, `ai4se-demo-project`, and
`naodeng.com.cn`; `ai-test-auditor` is an extra TypeScript/Node case); at least
30 real obligations; and time to first value of 10 minutes or less. The paired
README must provide verified installation, quick-start, usage, configuration,
and troubleshooting paths. See [roadmap](roadmap.md).

The 1.0 impact contract accepts either repeated repository-relative
`--changed-file` values or local `--base` / `--head` snapshots. Direct mode
reports affected obligations and leaves gap delta unassessed; snapshot mode
computes `newGaps` and `resolvedGaps`. Path globs are explicit and deterministic;
package/module/service/API mappings must be expanded to paths by the caller.
The core protocol remains `qcov.dev/v1alpha1`; `qcov.impact/v1` and
`qcov.adapter/v1` are additive contracts.

## Still excluded without a new approved design

Web UI, database persistence, remote Git operations, automatic
inventory-to-obligation inference, policy DSL, dimension thresholds, wildcard
or path-based waivers, and coverage/LCOV promotion to covering passed evidence
remain out of scope until separately approved. Adapter SDK v1 is planned for
QCov 1.0; broader ecosystem/plugin loading, QA for AI, Quality BOM, and
Continuous Quality Control Plane packaging require later designs.

## Pending requirement: broader mapping

Limited trailing `*` identity wildcards and pytest-marker evaluation merge are
part of Iteration 5. Coverage/LCOV still must not auto-promote to covering
evidence. Unmapped generic imports stay diagnostics and inventory only.
