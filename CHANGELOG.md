# Changelog

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
