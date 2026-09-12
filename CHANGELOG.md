# Changelog

## 1.0.0 - 2026-09-12

### Features

- Add deterministic Change-to-Obligation impact analysis with stable
  `qcov.impact/v1` reports and the `qcov impact` / `qcov affected` commands.
- Add the public `qcov.adapter/v1` Adapter SDK and a JaCoCo inventory adapter.
- Add reviewed real-project case studies for pytest, JUnit/JaCoCo, and
  Playwright, with explicit evidence mappings and reproducible fixtures.

### Documentation

- Add bilingual installation and getting-started guides, protocol updates, and
  case-study documentation; retain a concise Chinese maintenance context for
  post-release reference.

### Boundaries

- Keep test reports, coverage, JaCoCo, LCOV, and static analysis as inventory
  unless an explicit mapping creates valid obligation-scoped evidence.

## 0.9.0 - 2026-09-11

### Features

- Add the local `production-observation` inventory adapter for versioned
  runtime, incident, and observability artifacts.
- Allow only explicit mappings from production observations to evidence and
  preserve the observation timestamp as the evidence execution timestamp.

### Boundaries

- Production observations remain inventory without a mapping; QCov does not
  execute services, access remote observability platforms, or infer obligations.

### Documentation

- Add bilingual production-evidence guidance and a runnable local example; mark
  Iteration 8 delivered.

## 0.8.0 - 2026-09-09

### Features

- Add Agentic Quality Loop helpers: required `qcov explain` and
  `qcov agent next`, plus optional `qcov agent validate-evidence`, under
  stable `contractVersion: qcov.agent/v1` JSON envelopes.
- Add deterministic explain reason codes and next-action selection that reuses
  `quality_plan` ranks (never a second scoring system).

### Boundaries

- Agent helpers do not run tests, write authoritative evidence, or change Gap /
  policy decisions. `validForLoad` is not COVERED and not policy PASS.

### Documentation

- Add bilingual agent playbook and mark Iteration 7 delivered on the roadmap.

## 0.7.0 - 2026-09-09

### Features

- Add deterministic `qcov plan`, which ranks unproven obligation dimensions
  with fixed benefit/cost heuristics and emits a draft `quality_plan` proposal
  for the next best verification work.
- Add stable `quality_plan`, `evaluation_gaps`, and `planned_verification`
  protocol values, including localized Markdown planning output.

### Boundaries

- Planning proposals remain local, deterministic, and proposal-only: they are
  never QualityEvidence and cannot change Gap Engine or policy decisions.

### Documentation

- Document Iteration 6 planner behavior, boundaries, and implementation
  verification evidence in the bilingual public docs and Chinese process record.

## 0.6.0 - 2026-09-08

### Features

- Merge pytest-marker observations into deterministic evaluation and support
  limited identity suffix wildcards in declarative mappings.
- Add offline, proposal-only `qcov obligation suggest` and `qcov risk analyze`;
  proposals are not evidence and cannot become gate authority.

### Documentation

- Document the Iteration 5 local/offline boundaries and proposal workflow.

## 0.5.0 - 2026-09-08

### Features

- Add deterministic local `qcov policy check` with explicit evaluation time,
  default coverage-status rules, expiring exact waivers, and PASS/WARN/BLOCK
  decisions.
- Add stable JSON and localized Markdown policy reports plus a runnable Refund
  policy fixture.

### Fixes

- Reject invalid policy format and locale values with stable input exit code 4,
  and identify expired waivers that require cleanup.

### Documentation

- Add Chinese-first policy reference, English README entry, process evidence,
  and Iteration 4 roadmap completion.

## 0.3.0 - 2026-09-06

### Features

- Add local Playwright JSON and LCOV inventory readers through a deterministic
  built-in adapter registry.

### Documentation

- Add Iteration 2 design, implementation, verification records, and runnable
  bilingual examples for the new report imports.

## 0.2.1 - 2026-09-06

### Fixes

- Classify an absent obligation inventory as `UNKNOWN` instead of `MISSING`.
- Generate a valid `QCovConfig` from `qcov init` and apply partial `--config`
  overrides independently.
- Exclude hidden dependency directories from pytest-marker discovery.

### Improvements

- Include observed evidence IDs in Markdown reports and pytest file/marker facts
  in scan output.
- Restore the `--obligations` compatibility alias and consolidate path
  resolution for configuration and scan diagnostics.

### Documentation

- Synchronize bilingual technical documentation, complete Iteration 1 tracking,
  and record the review remediation TDD evidence.
