# Get started in five minutes

QCov is a local, deterministic evidence-gap engine. It evaluates explicit
`TestingObligation` and `QualityEvidence` records; it does not run test suites,
infer obligations from test names, or make AI a gate authority.

This walkthrough uses checked-in fixtures, so every command is executable from
the repository root. It covers the current `gaps → scan → map preview → gaps →
local Git change impact → policy check` workflow.

## 1. Install QCov

QCov requires Python 3.11+. The tool is a Python CLI even when the project
being observed is Java or TypeScript.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

Use `.venv/bin/python -m qcov` below to avoid relying on a shell entry-point
path.

## 2. See an evidence gap

```bash
.venv/bin/python -m qcov gaps \
  --obligation examples/refund/obligation.yaml \
  --evidence examples/refund/evidence
```

The result is intentionally `PARTIAL`: the Refund fixture has behavior,
boundary, and data evidence, but no concurrency, idempotency, or production
evidence. `gaps` reports facts; it does not block a build.

## 3. Scan local artifacts without running tests

```bash
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml
```

`scan` reads declared local paths only. This fixture scans JUnit XML,
coverage.py XML, Playwright JSON, and LCOV. It never executes pytest, Maven,
Gradle, npm, or Playwright.

## 4. Preview an explicit mapping, then evaluate it

```bash
.venv/bin/python -m qcov map preview \
  --config examples/imported-reports/qcov.yaml --format json

.venv/bin/python -m qcov gaps --config examples/imported-reports/qcov.yaml
```

The preview is read-only. `mappings/refund.yaml` explicitly maps selected JUnit
and Playwright identities to `QualityEvidence`; `gaps --config` then merges
authored evidence, explicit pytest-marker evidence, and those mapping results.

## 5. Inspect change impact in committed Git snapshots

`qcov impact` maps changed repository paths to explicit obligations. With two
local Git snapshots it also reports deterministic `newGaps` and `resolvedGaps`.
`qcov affected` reports only the currently non-covered affected obligations.
Run the self-contained diff demo:

```bash
.venv/bin/python examples/pr-delta/demo.py
```

For your repository, commit the relevant `qcov.yaml`, obligation, and evidence
files first, then use:

```bash
.venv/bin/python -m qcov diff \
  --repo . --base origin/main --head HEAD --config qcov.yaml
```

To run Impact, keep `qcov.yaml` and a `QualityImpactConfig` path mapping in the
repository, then use either repeated `--changed-file` values or a local Git
snapshot pair (never both):

```bash
.venv/bin/python -m qcov impact \
  --config qcov.yaml --impact-config impact.yaml \
  --repo . --base origin/main --head HEAD --format json
```

It reads Git objects only: it does not fetch, check out commits, run tests, or
read dirty/untracked files.

## 6. Apply a reproducible local policy

```bash
.venv/bin/python -m qcov policy check \
  --config examples/imported-reports/qcov.yaml \
  --policy examples/refund/policy.yaml \
  --as-of 2026-09-07T00:00:00+08:00
```

This fixture exits `0`: its intentional `PARTIAL` has a valid, expiring waiver.
Policy evaluates the already-computed status and never changes evidence or
coverage facts. Exit `2` means `BLOCK`; exit `4` means invalid input.

## Language-specific entry points

| Project | Produce locally | Declare in QCov | Authority boundary |
| --- | --- | --- | --- |
| Python | Run pytest and, if desired, create coverage.py XML outside QCov. | Use explicit `@pytest.mark.qcov` evidence or authored YAML; list coverage.py under `scan.coverage`. | A marker or authored `QualityEvidence` is eligible evidence; coverage.py is inventory-only. |
| Java | Run JUnit/JaCoCo outside QCov and retain JUnit XML. | List JUnit XML under `scan.junit`; map selected identities with `EvidenceMapping`. | Only an explicit JUnit mapping produces `QualityEvidence`; JaCoCo/LCOV-style rates are not covering evidence. |
| TypeScript | Run Playwright outside QCov and retain its JSON report. | List it under `scan.playwright`; map selected identities with `EvidenceMapping`. | Only an explicit Playwright mapping produces `QualityEvidence`; test names alone do not infer obligations. |

The initial configuration can be created without overwriting an existing file:

```bash
.venv/bin/python -m qcov init --path .
```

Then add only paths for artifacts your existing Python, Java, or TypeScript
toolchain already produces. See [explicit mapping](mapping.md) and
[policy gates](policy.md) for the schema and diagnostics.

## Troubleshooting and authority boundaries

- **`QCOV-CONFIG-*` or exit `4`:** a config path, protocol document, mapping,
  or policy input is invalid. Check that declared paths exist relative to
  `qcov.yaml` and that `--as-of` includes a timezone.
- **`PARTIAL`, `MISSING`, or `UNKNOWN`:** these are evaluation results, not a
  scanner failure. Use `qcov explain` to inspect one gap; add or correct real
  evidence rather than changing a status manually.
- **A scan found a test report but gaps did not change:** inventory is not
  authority. Add an explicit mapping for JUnit/Playwright, or author a
  `QualityEvidence` record. `coverage.py` and LCOV cannot be promoted through
  a mapping.
- **A policy blocks:** inspect its result and waiver expiry. `policy check`
  decides a local gate from authoritative evaluation results; it does not make
  scanner records, AI proposals, `qcov plan`, or `qcov agent` output authoritative.
- **The Git comparison misses uncommitted work:** this is expected. Commit the
  QCov inputs and rerun `qcov diff`; it deliberately ignores dirty files.

AI proposal commands and agent helpers can explain or suggest work, but never
become evidence or policy/gate authority.
