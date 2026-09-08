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
an explicit obligation mapping exists. `qcov diff` compares explicit obligation
and evidence snapshots across local committed revisions. `qcov policy check`
applies local deterministic gates with exact, expiring waivers and an explicit
`--as-of` timestamp.

## Still excluded without a new approved design

AI providers, web UI, database persistence, remote Git operations, external
plugin loading, inventory-to-evidence inference, policy DSL, dimension
thresholds, and wildcard or path-based waivers remain out of scope.

## Pending requirement: explicit mapping

A declared mapping layer must be able to turn selected inventory observations
into `QualityEvidence` without weakening the explicit-evidence model. Until that
lands, generic imports stay diagnostics and inventory only.
