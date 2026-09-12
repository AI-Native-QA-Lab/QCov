# QCov

> **Find what your tests still don't prove.**

[中文](README.zh-CN.md) · [Get started](docs/en/getting-started.md) · [Concepts](docs/en/concepts.md) · [Agent](docs/en/agent.md) · [Roadmap](docs/en/roadmap.md) · [Contributing](CONTRIBUTING.md)

QCov is an open-source **Quality Evidence Gap Engine** and **Quality Coverage
Protocol**. It does not replace pytest, JUnit, Playwright, coverage tools,
security scanners, or observability platforms. It asks whether evidence from
those tools proves a requirement, risk, or change.

## Features

- Deterministic gap evaluation: `COVERED`, `PARTIAL`, `MISSING`, `UNKNOWN`
- Local inventory scan for pytest markers, JUnit, coverage.py, Playwright (`scan.playwright`), LCOV (`scan.lcov`), and production observations (`scan.production`)
- Explicit `EvidenceMapping` from junit/playwright/production-observation inventory to `QualityEvidence`
- Local `qcov diff` across committed Git trees
- Local `qcov policy check` with exact, expiring waivers
- Proposal-only assistants: `qcov obligation suggest`, `qcov risk analyze`, and
  deterministic `qcov plan` (draft `QualityProposal`; never evidence or gate
  authority)
- Markdown and JSON reports with `en` / `zh-CN` presentation

Not included: AI gate decisions, web UI, database persistence, remote Git host
APIs, external plugins, or promoting coverage/LCOV line rates to covering
evidence.

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

For a five-minute, executable `gaps → scan → map preview → gaps → local Git
change impact → policy check` walkthrough, including Python, Java/JUnit, and
TypeScript/Playwright entry points, read the [getting-started guide](docs/en/getting-started.md).
It also explains why `coverage.py` and LCOV are inventory-only, and which
records are authoritative evidence.

## Usage

```bash
# Discover local report inventory (no test execution)
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml

# Preview declarative inventory → evidence mappings
.venv/bin/python -m qcov map preview \
  --config examples/imported-reports/qcov.yaml --format json

# Evaluate gaps with config defaults and optional mappings
.venv/bin/python -m qcov gaps --config examples/imported-reports/qcov.yaml

# Compare committed obligation/evidence snapshots (the current local Git impact view)
.venv/bin/python -m qcov diff --base origin/main --head HEAD --config qcov.yaml

# Local policy gate
.venv/bin/python -m qcov policy check \
  --config examples/imported-reports/qcov.yaml \
  --policy examples/refund/policy.yaml \
  --as-of 2026-09-07T00:00:00+08:00

# Draft obligation / change-risk proposals (offline by default; not evidence)
.venv/bin/python -m qcov obligation suggest \
  --config qcov.yaml --requirements requirements.md --format json
.venv/bin/python -m qcov risk analyze \
  --config qcov.yaml --base HEAD~1 --head HEAD --format json
```

See the [imported-reports example](examples/imported-reports/README.md),
[mapping guide](docs/en/mapping.md), [PR delta](docs/en/pr-delta.md), and
[policy gates](docs/en/policy.md), and [production evidence](docs/en/production-evidence.md).

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
