# QCov

> **Find what your tests still don't prove.**

[中文](README.zh-CN.md) · [Concepts](docs/en/concepts.md) · [Roadmap](docs/en/roadmap.md) · [Contributing](CONTRIBUTING.md)

QCov is an open-source **Quality Evidence Gap Engine** and **Quality Coverage
Protocol**. It does not replace pytest, JUnit, Playwright, coverage tools,
security scanners, or observability platforms. It asks whether evidence from
those tools proves a requirement, risk, or change.

## Features

- Deterministic gap evaluation: `COVERED`, `PARTIAL`, `MISSING`, `UNKNOWN`
- Local inventory scan for pytest markers, JUnit, coverage.py, Playwright (`scan.playwright`), and LCOV (`scan.lcov`)
- Explicit `EvidenceMapping` from junit/playwright inventory to `QualityEvidence`
- Local `qcov diff` across committed Git trees
- Local `qcov policy check` with exact, expiring waivers
- Markdown and JSON reports with `en` / `zh-CN` presentation

Not included: AI decisions, web UI, database persistence, remote Git, external
plugins, or promoting coverage/LCOV line rates to covering evidence.

## Installation

Requires Python 3.11+.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## Quick start

```bash
.venv/bin/python -m qcov gaps \
  --obligation examples/refund/obligation.yaml \
  --evidence examples/refund/evidence
```

The Refund example reports `PARTIAL`: behavior, boundary, and data evidence
exist; concurrency, idempotency, and production evidence remain unproven.

## Usage

```bash
# Discover local report inventory (no test execution)
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml

# Preview declarative inventory → evidence mappings
.venv/bin/python -m qcov map preview \
  --config examples/imported-reports/qcov.yaml --format json

# Evaluate gaps with config defaults and optional mappings
.venv/bin/python -m qcov gaps --config examples/imported-reports/qcov.yaml

# Compare committed obligation/evidence snapshots
.venv/bin/python -m qcov diff --base origin/main --head HEAD --config qcov.yaml

# Local policy gate
.venv/bin/python -m qcov policy check \
  --config qcov.yaml --policy policy.yaml \
  --as-of 2026-09-07T00:00:00+08:00
```

See the [imported-reports example](examples/imported-reports/README.md),
[mapping guide](docs/en/mapping.md), [PR delta](docs/en/pr-delta.md), and
[policy gates](docs/en/policy.md).

## Documentation

- [Requirements](docs/en/requirements.md)
- [Architecture](docs/en/architecture.md)
- [Protocol](docs/en/protocol.md)
- [Technical design](docs/en/technical-design.md)
- [Development guide](docs/en/development.md)
- [Explicit evidence mapping](docs/en/mapping.md)
- [PR Quality Coverage Delta](docs/en/pr-delta.md)
- [Process records](docs/en/process.md)

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md). Use
test-first development and run `pytest`, `ruff check .`, `mypy qcov`,
`python -m build`, and `git diff --check` before reporting completion.

## License

[PolyForm Noncommercial License 1.0.0](LICENSE).
