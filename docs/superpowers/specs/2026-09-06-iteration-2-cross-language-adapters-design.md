# Iteration 2 Cross-Language Adapters Design

## Goal

Add side-effect-free inventory readers for Playwright JSON and LCOV trace files,
and replace the hard-coded scan list with one explicit built-in adapter registry.

## Scope

`scan.playwright` accepts files emitted by Playwright's JSON reporter. The
adapter traverses nested suites and emits one inventory record per project test
outcome. Its identity is the report-relative file plus spec title; its status
is Playwright's aggregated test status (`expected`, `unexpected`, `flaky`, or
`skipped`).

`scan.lcov` accepts LCOV trace files. For each `SF:` section it counts `DA:`
lines and non-zero execution counts and emits one `observed` record with
`instrumentedLines` and `hitLines` metadata. The reader accepts optional
checksums and ignores unrelated LCOV fields. A malformed JSON document, a
missing `SF:` before `DA:`, or an unterminated source section is a non-fatal
`QCOV-SCAN-001` diagnostic.

The registry owns the deterministic order of built-in report readers:
`coverage.py`, `junit`, `lcov`, and `playwright`. Pytest marker discovery stays
separate because it scans source files rather than a configured report. No
third-party adapter loading is added.

## Invariants

- All inputs remain local, read-only, and are never executed or imported.
- Inventory records never infer obligation IDs or create `QualityEvidence`.
- Missing configured reports and malformed reports remain diagnostics; invalid
  configuration remains `QCOV-CONFIG-001` and CLI exit 4.
- JSON keys, config keys, adapters, and diagnostic codes remain English.
- Explicit report paths are resolved relative to `qcov.yaml`, sorted, and
  deduplicated as before.

## Validation

Focused tests cover nested Playwright suites, all four outcomes, malformed
JSON, LCOV count aggregation, malformed LCOV, registry order, config
resolution, and CLI JSON output. The release gate runs pytest, Ruff, mypy,
build, runnable examples, and `git diff --check`.
