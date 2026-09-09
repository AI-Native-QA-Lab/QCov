# Requirements

## Core engine

The product accepts versioned obligation and evidence files, validates them,
computes four states per obligation (`COVERED`, `PARTIAL`, `MISSING`,
`UNKNOWN`), and renders JSON or Markdown. Exact passed evidence must match
obligation ID, dimension, and required type. No aggregate quality score is
calculated. `UNKNOWN` must never masquerade as a pass.

## Delivered local capabilities

Config-driven `scan` discovers pytest markers and imports JUnit XML,
coverage.py XML, Playwright JSON, and LCOV as **inventory observations** until
an explicit obligation mapping exists. Iteration 4.5 provides declarative
`EvidenceMapping` for junit/playwright identities, `qcov map preview`, and
`--config` evaluation merge. `qcov diff` compares explicit obligation and
evidence snapshots across local committed revisions. `qcov policy check`
applies local deterministic gates with exact, expiring waivers and an explicit
`--as-of` timestamp.

## Delivered through Iteration 6 (proposal layer)

Iteration 5 adds mapping hardening (pytest-marker evaluation wiring and limited
identity DX) plus proposal-only AI (`obligation suggest`, `risk analyze`).
Iteration 6 adds deterministic `qcov plan` (fixed benefit/cost heuristics over
unproven gaps → draft `QualityProposal` with `type: quality_plan`). Proposals
never become evidence or gate authority.

## Planned Iterations 7–8

Iteration 7 adds an Agentic Quality Loop. Iteration 8 adds production evidence
producers under the same protocol rules. AI/plan proposals never become evidence
or gate authority. See [roadmap](roadmap.md).

## Still excluded without a new approved design

Web UI, database persistence, remote Git operations, external plugin loading,
inventory-to-obligation inference, policy DSL, dimension thresholds,
wildcard or path-based waivers, and coverage/LCOV promotion to covering passed
evidence remain out of scope until separately approved. Post-8 topics (QA for
AI, Quality BOM, Adapter SDK, Continuous Quality Control Plane packaging) also
require new designs.

## Pending requirement: broader mapping

Limited trailing `*` identity wildcards and pytest-marker evaluation merge are
part of Iteration 5. Coverage/LCOV still must not auto-promote to covering
evidence. Unmapped generic imports stay diagnostics and inventory only.
