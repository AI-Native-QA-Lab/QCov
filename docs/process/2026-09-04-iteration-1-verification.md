# Iteration 1 Evidence Import Verification Record

## Scope

This record closes the approved Iteration 1 plan:
`docs/superpowers/plans/2026-09-04-iteration-1-evidence-import.md`.

## Delivered

- Strict `QCovConfig` v1alpha1 loader, relative path/glob resolution, and JSON
  Schema.
- Side-effect-free pytest marker detection, JUnit XML inventory, and coverage.py
  XML inventory.
- `qcov scan --config` Markdown/JSON discovery diagnostics.
- `--config` defaults for `gaps`, `check`, and `report`.
- Imported-reports fixture, paired English/Chinese documentation, ADR 0003, and
  a Mermaid data-flow diagram.

## TDD and executed verification

Each feature task has a dated process record documenting its initial RED failure
and subsequent GREEN result. On 2026-09-04 (Asia/Shanghai), final validation
passed:

```text
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml               # 3 adapters, 3 records
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml --format json # passed
.venv/bin/python -m qcov gaps --config examples/imported-reports/qcov.yaml               # QO-REFUND-001 PARTIAL
.venv/bin/ruff check .                                                                     # passed
.venv/bin/mypy qcov                                                                        # 20 source files, no issues
.venv/bin/python -m pytest                                                                 # 32 passed
.venv/bin/python -m build                                                                  # sdist and wheel built
git diff --check                                                                           # passed
```

## Limits retained

JUnit/coverage imports are inventory only. They never infer an obligation,
produce passed Quality Evidence, execute user tests, or calculate a quality
score. JaCoCo, Playwright, external adapters, policy, Git delta, and AI remain
future roadmap items.

## Fixture tracking correction

The repository-wide Python ignore rule initially excluded the intentional
`examples/imported-reports/coverage.xml` fixture. A narrow negation rule now
tracks that single documented sample while preserving normal generated coverage
report ignores. The fixture was rechecked with `git check-ignore` before commit.
