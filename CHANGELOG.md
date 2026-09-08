# Changelog

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
