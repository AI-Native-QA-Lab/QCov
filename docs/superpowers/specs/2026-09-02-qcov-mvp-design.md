# QCov MVP Design Specification

## Purpose

QCov is an open-source **Quality Evidence Gap Engine** and **Quality Coverage
Protocol**. It answers a question that test runners and coverage tools do not:

> What remains unproven for a requirement, risk, or code change?

The first release is a deterministic, local CLI. It accepts machine-readable
testing obligations and evidence, calculates explainable evidence gaps, and
renders human- and machine-readable reports. It is not a test-management
system, static-analysis engine, dashboard, database platform, or AI test
generator.

## Product Scope

### Iteration 0 deliverable

The repository must provide a working Python 3.11+ package and `qcov` CLI with:

- versioned JSON Schemas for `TestingObligation`, `QualityEvidence`, and
  `QualityPolicy`;
- YAML/JSON loading with schema validation;
- a deterministic gap engine that produces `COVERED`, `PARTIAL`, `MISSING`, or
  `UNKNOWN` per obligation and required evidence dimension;
- an inspectable Refund reference scenario, including manually authored
  evidence and intentional missing concurrency, idempotency, and production
  evidence;
- Markdown and JSON reports;
- English-default CLI output with a `--locale zh-CN` presentation switch;
- a minimal adapter protocol and a pytest-marker reference adapter; and
- automated tests for schemas, loading, status calculation, reports, CLI, and
  locale-sensitive presentation.

The implementation deliberately excludes AI providers, Git-diff delta,
database persistence, web UI, policy enforcement, remote telemetry, and all
adapters except the marker-based pytest reference adapter. Those features have
documented future homes but no stubbed runtime behavior.

### Success criteria

Given valid obligations plus observed evidence, QCov consistently computes an
explainable status. A developer can clone the repository, install development
dependencies, run the Refund example, and see why the result is partial. The
project documents a 10-minute first-value path without claiming that adapters
not shipped by the MVP are available.

## Architecture

```text
Obligation YAML/JSON ─┐
                      ├─> loaders + schemas ─> domain models ─> gap engine
Evidence YAML/JSON ───┘                                      │
                                                              ├─> JSON report
pytest marker adapter ─> Evidence IR ─────────────────────────└─> Markdown report
                                                                    │
                                                              CLI + i18n catalog
```

The core only consumes QCov's language-neutral Evidence IR. Input readers,
adapters, formatting, and command parsing sit at the edge. This preserves a
small deterministic engine and lets future language/tool adapters normalize
their output without coupling the core to pytest, JUnit, or Playwright.

### Domain rules

`TestingObligation` has a stable ID, localized title, source, risk, optional
invariants, and `requiredEvidence`: a mapping from quality dimension to one or
more acceptable evidence types. `QualityEvidence` references exactly one
obligation and declares dimension, type, producer, status, timestamp, artifact,
and confidence metadata.

For each required dimension:

- `COVERED`: at least one matching evidence item has status `passed`.
- `MISSING`: evidence is present for the obligation but no matching item exists
  for that required dimension/type.
- `UNKNOWN`: no usable observation can determine the dimension because the
  evidence inventory is absent or marked unknown.

An obligation is `COVERED` only when every required dimension is covered;
`MISSING` when no required dimension is covered and every dimension is known
missing; `PARTIAL` when it has a mixture of covered and missing/unknown
dimensions; and `UNKNOWN` when every required dimension is unknown. Reports
must list the requirement, observed evidence, required evidence, missing or
unknown dimensions, and the resulting status rather than emit a composite score.

Failed or skipped evidence is retained in reports but never satisfies required
evidence. The MVP does not infer whether a test proves an obligation: explicit
IDs and adapter output are the authoritative mapping.

## Repository Layout

```text
qcov/
├── qcov/                    # installable Python package
│   ├── cli/                 # Typer commands and presentation glue
│   ├── engine/              # deterministic gap calculation and reporting
│   ├── models/              # Pydantic domain and protocol models
│   ├── adapters/            # adapter protocol and pytest reference adapter
│   └── i18n/                # en and zh-CN message catalogs
├── schemas/                 # published JSON Schema files
├── examples/refund/         # runnable obligations, evidence, policy, README
├── tests/                   # unit and CLI integration tests
├── docs/
│   ├── en/                  # English product and engineering documentation
│   ├── zh-CN/               # Chinese counterparts
│   ├── diagrams/            # source-controlled Mermaid architecture diagrams
│   └── superpowers/         # design specs and implementation plans
├── .github/workflows/       # format, type/test, package CI
├── README.md                # English first; links to README.zh-CN.md
├── README.zh-CN.md          # Chinese entry point
├── AGENTS.md                # repository-local contributor/agent rules
└── pyproject.toml           # packaging, tools, test configuration
```

Each implementation unit has one responsibility: models define validated data,
the engine evaluates it, adapters produce normalized data, and the CLI binds
files/options to output. Documentation follows the same separation: user
concepts, requirements, architecture, technical decisions, developer workflow,
and roadmap are separate bilingual pages.

## CLI Contract

The initial commands use a shared `--locale {en,zh-CN}` option and support
`--format {markdown,json}` where applicable.

```text
qcov init [--path PATH]
qcov scan [--path PATH] [--format markdown|json]
qcov gaps [--obligations PATH] [--evidence PATH] [--format markdown|json]
qcov inspect OBLIGATION_ID [--obligations PATH] [--evidence PATH]
qcov check [--obligations PATH] [--evidence PATH]
qcov report [--obligations PATH] [--evidence PATH] [--output PATH]
```

`init` writes only a sample configuration into a user-selected empty directory
or exits with a stable error code if a configuration already exists. `scan`
uses only installed/local adapters and reports detected inputs; in Iteration 0
the pytest adapter recognizes explicit `@pytest.mark.qcov("QO-...")` markers.
`check` exits nonzero when an obligation is `MISSING` or `PARTIAL`; `UNKNOWN`
is reported distinctly and does not masquerade as a pass. Exact exit-code
policy is documented and tested.

## Protocol and Extensibility

Machine keys and enum values are English. Human-facing fields use a localized
object such as `{ "en": "...", "zh-CN": "..." }`. Stable error identifiers
use `QCOV-<AREA>-<NUMBER>` and are translated only at presentation time.

The adapter SDK is intentionally small:

```python
class Adapter(Protocol):
    name: str

    def detect(self, project_path: Path) -> DetectionResult: ...
    def collect(self, project_path: Path) -> list[QualityEvidence]: ...
```

Adapters must not calculate coverage or gates. They normalize producer output
into Evidence IR and declare diagnostics. External plugin loading is deferred
until Iteration 2; the initial package registers built-in adapters explicitly.

## Documentation and Localization

`README.md` is English-first and contains an adjacent `中文` link to
`README.zh-CN.md`; the Chinese README links back to English. Every canonical
document in `docs/en/` has an equivalent file in `docs/zh-CN/`, with identical
heading hierarchy, file stem, protocol terms, commands, and lifecycle claims.
English remains authoritative for machine-facing identifiers; Chinese explains
them but does not translate YAML keys, CLI flags, code identifiers, or error
codes.

The repository documents:

- product concept and non-goals;
- MVP requirements, terminology, and acceptance criteria;
- architecture and Mermaid diagrams;
- protocol, schema, evidence status, and adapter design;
- local development, tests, release expectations, and contribution rules;
- the Iteration 0–8 roadmap, 3/6/12-month outlook, validation hypotheses,
  success metrics, risks, and future AI/production directions.

## Quality Strategy

Tests use pytest and run without network access. Unit tests cover each status
rule, incompatible dimension/type combinations, invalid schema versions,
missing obligation references, localized messages, and report content. CLI
tests execute the installed command with temporary input fixtures. CI runs
format/lint checks, unit tests, and package build. The README quickstart is
backed by the Refund fixture so documented output is reproducible.

## Delivery Sequence

1. Create packaging, repository rules, bilingual navigation, and CI baseline.
2. Define protocol models, JSON Schemas, example fixtures, and validation tests.
3. Implement the deterministic engine and structured reporting.
4. Build the CLI and reference pytest adapter with end-to-end command tests.
5. Complete bilingual product/technical/developer documentation and diagrams.
6. Validate clean install, CLI quickstart, full tests, schema fixtures,
   formatting, and build.

## Deferred Roadmap

Iteration 1 makes the CLI broadly usable and imports common files. Iteration 2
adds multi-language adapters and an SDK. Iteration 3 introduces `qcov diff` and
PR Quality Coverage Delta. Iteration 4 adds policy, waivers, and hard gates.
Iterations 5–7 introduce AI only as a proposal/planning layer under
deterministic policy checks. Iteration 8 integrates production evidence.

The project validates five assumptions before accelerating: Testing Obligations
add value beyond requirement-to-test traceability; initial integration is fast;
gaps are explainable; the tool finds evidence omissions that ordinary reports
hide; and AI proposals never become evidence or gate authority.
