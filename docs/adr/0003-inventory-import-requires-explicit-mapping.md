# ADR 0003: Keep imported inventory separate from quality evidence

## Status

Accepted — 2026-09-04.

## Decision

Generic pytest, JUnit XML, and coverage.py imports create inventory observations
and scan diagnostics only. They do not create obligation-satisfying
`QualityEvidence` unless a future explicit mapping layer supplies the
relationship.

## Consequences

QCov avoids claiming that a passing test, recognizable class, or high line rate
proves a requirement. The first-value experience still surfaces available data
and missing integration inputs without test execution.
