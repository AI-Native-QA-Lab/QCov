# QCov Iteration 1 Evidence Import Design Specification

## Purpose

Iteration 1 makes QCov useful on an existing repository without requiring all
evidence to be authored manually. It discovers local test-report artifacts,
normalizes a deliberately narrow set of common formats into Evidence IR, and
loads project defaults from `qcov.yaml`.

The goal is a reproducible first-value experience: a user can run `qcov scan`
against a local project, see candidate inputs and diagnostics, configure only
the critical obligation mapping that is not already explicit, and then use the
existing gap/report commands.

## Scope

### Included

- `qcov scan` detection for pytest marker source, JUnit XML, and coverage.py
  XML reports.
- A generic JUnit XML adapter that reads testcase outcomes without executing a
  test suite.
- A coverage.py XML adapter that records structural coverage observations.
- A project configuration loader for `qcov.yaml` with obligation, evidence, and
  report-input path lists.
- `scan --format markdown|json`, deterministic diagnostics, and stable error
  codes.
- A Python sample project plus a JUnit XML fixture to exercise first-value
  flows.
- Matched English/Chinese docs, an ADR, process records, and tests.

### Excluded

- JUnit-specific semantic inference, JaCoCo/PIT/Playwright/SonarQube imports,
  external adapter plugin discovery, remote calls, test execution, automatic
  obligation creation, Git delta, policies, and AI.

## Architecture

```text
qcov.yaml / CLI paths ─> project configuration ─> artifact discovery
                                                     │
                   ┌───────────────┬─────────────────┴───────────────┐
                   ▼               ▼                                 ▼
           pytest marker      JUnit XML                         coverage.py XML
                   │               │                                 │
                   └───────────────┴─────> Evidence IR / diagnostics ┘
                                                     │
                                                     ▼
                                          existing Gap Engine / Reporter
```

Adapters remain producers: they neither decide a gap status nor claim that a
test proves a business obligation. An imported item that has no explicit
obligation mapping stays an inventory observation. It can be shown by `scan`
but cannot satisfy required evidence until an obligation reference exists.

## Data Model

`ProjectConfig` is a strict Pydantic model with:

```yaml
apiVersion: qcov.dev/v1alpha1
kind: QCovConfig
obligations:
  - qcov/obligations/*.yaml
evidence:
  - qcov/evidence/*.yaml
scan:
  junit:
    - reports/junit.xml
  coverage:
    - coverage.xml
```

All paths are interpreted relative to the configuration file. Glob expansion is
sorted and deduplicated. Missing configured artifacts produce diagnostics, not
an exception, so `scan` can explain an incomplete setup. Missing obligation or
evidence input requested by `gaps`/`check` is still a stable configuration
error.

The JUnit XML adapter emits an inventory record per `<testcase>`, with producer
`junit`, status mapped from `<failure>`, `<error>`, or `<skipped>`, and an
artifact path/identity. The coverage.py adapter reads package/class line-rate
metadata and emits structural observations with producer `coverage.py`. Since
neither generic report carries an obligation relationship, both use no
`QualityEvidence` record until a future explicit mapping layer is added.

## CLI Contract

```text
qcov scan [--path PATH] [--config PATH] [--format markdown|json]
qcov gaps [--config PATH] [--obligation PATH] [--evidence PATH] ...
qcov check [--config PATH] [--obligation PATH] [--evidence PATH] ...
qcov report [--config PATH] [--obligation PATH] [--evidence PATH] ...
```

`scan` returns zero when it can inspect a project, even if some configured
artifacts are missing; malformed config returns code 4. Its Markdown output
lists each adapter, detection state, files, record count, and diagnostic. JSON
uses stable English keys.

When `--config` is supplied, `gaps`, `check`, and `report` take the first
resolved obligation path and every resolved evidence path unless explicit CLI
arguments override those selections. The MVP maintains one obligation per
command to avoid silently aggregating unrelated gaps.

## Error Handling and Trust Boundaries

- Parse JUnit/coverage XML using only the standard library; malformed XML is a
  non-fatal scan diagnostic.
- Never run a project test command or import project code.
- Never interpret test names, package names, or coverage values as proof of a
  requirement.
- Use stable errors `QCOV-CONFIG-001` for invalid configuration and
  `QCOV-SCAN-001` for unreadable/invalid artifacts.

## Test Strategy

Tests cover config relative paths/globs, malformed configuration, missing
configured artifacts, JUnit outcome mapping, coverage XML metadata reading,
scan JSON/Markdown stability, CLI configuration precedence, and no-execution
guarantees. The existing 20-test MVP suite remains green; CI continues to run
all tests across Python 3.11 and 3.12.

## Documentation and Acceptance Criteria

The paired docs explain supported versus planned formats and contain a literal
quickstart using the sample fixture. Acceptance is met when a clean local
installation can:

1. execute `qcov scan` against the sample fixture;
2. identify pytest/JUnit/coverage inputs with explainable diagnostics;
3. parse the project config and apply paths to an existing `qcov gaps` flow;
4. produce equivalent JSON and localized Markdown facts; and
5. pass tests, Ruff, mypy, package build, and `git diff --check`.
