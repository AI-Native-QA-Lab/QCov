# QCov

> **Find what your tests still don't prove.**

[中文](README.zh-CN.md) · [Concepts](docs/en/concepts.md) · [Roadmap](docs/en/roadmap.md) · [Contributing](CONTRIBUTING.md)

QCov is an open-source **Quality Evidence Gap Engine** and **Quality Coverage
Protocol** for AI-native software delivery. It does not replace pytest, JUnit,
Playwright, coverage tools, security scanners, or observability. It asks whether
the evidence from those tools proves a requirement, risk, or change.

## MVP

The local deterministic MVP validates Testing Obligations and Quality Evidence,
then reports `COVERED`, `PARTIAL`, `MISSING`, or `UNKNOWN`. It intentionally
does not include AI, a database, a dashboard, Git delta, or policy gates.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m qcov gaps \
  --obligation examples/refund/obligation.yaml \
  --evidence examples/refund/evidence
```

The Refund scenario reports `PARTIAL`: behavior, boundary, and data evidence
exist; concurrency, idempotency, and production evidence are still unproven.

To discover existing local reports without executing them, run
`qcov scan --config examples/imported-reports/qcov.yaml`. Use `--format json`
for machine-readable inventory facts. See the [imported-reports example](examples/imported-reports/README.md).

## Project map

- [Requirements](docs/en/requirements.md)
- [Architecture](docs/en/architecture.md)
- [Protocol](docs/en/protocol.md)
- [Technical design](docs/en/technical-design.md)
- [Development guide](docs/en/development.md)
- [Process records](docs/en/process.md)

## License

[PolyForm Noncommercial License 1.0.0](LICENSE).
