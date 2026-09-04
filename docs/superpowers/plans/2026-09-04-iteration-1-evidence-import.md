# QCov Iteration 1 Evidence Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add local config-driven discovery and explainable pytest/JUnit XML/coverage.py report imports without weakening QCov's explicit-evidence model.

**Architecture:** Strict project configuration resolves local paths and feeds three side-effect-free artifact readers. `scan` returns inventory diagnostics, while only explicitly mapped manual evidence continues into the Gap Engine.

**Tech Stack:** Python 3.11+, Pydantic v2, PyYAML, stdlib XML, Typer, pytest, Ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-09-04-iteration-1-evidence-import-design.md`

## Global Constraints

- [ ] Parse artifacts locally and never execute/import user project code.
- [ ] Keep generic imported test/coverage observations separate from obligation-satisfying `QualityEvidence`.
- [ ] Retain English protocol keys and JSON output; localize Markdown only.
- [ ] Treat malformed/missing scan artifacts as diagnostics, but invalid config as `QCOV-CONFIG-001` / exit 4.
- [ ] Update paired English/Chinese docs and a dated process record per delivered task.
- [ ] Follow strict TDD for every behavior: write one focused test first, run it
      and observe the expected RED failure, write only the smallest production
      implementation needed for GREEN, then run scoped and full regression.
      Process records must preserve the RED/GREEN evidence.

---

## Task 1: Config Model, Relative Path Resolution, and Schema

**Files:** Create `qcov/models/config.py`, `schemas/config.schema.json`, `tests/models/test_config.py`; modify `qcov/models/__init__.py`, `qcov/models/io.py`, `AGENTS.md`.

**Interfaces:** Produces `ProjectConfig`, `load_config(path)`, and `resolve_paths(config, config_path)` returning sorted, deduplicated `Path` values.

- [ ] **Step 1: Write failing config tests.**

```python
def test_config_resolves_relative_globs_in_sorted_order(tmp_path: Path) -> None:
    config = write_config(tmp_path, "evidence: [reports/*.yaml]")
    assert [path.name for path in resolve_paths(load_config(config), config).evidence] == ["a.yaml", "b.yaml"]
```

- [ ] **Step 2: Run `pytest tests/models/test_config.py -q`.** Expected: FAIL because the config API does not exist.
- [ ] **Step 3: Implement strict `QCovConfig` v1alpha1 model, loader, resolution, and generated schema.** Add the strict RED/GREEN TDD requirement to `AGENTS.md`. Missing matched artifact paths remain a diagnostic candidate rather than a loader exception.
- [ ] **Step 4: Run model tests, Ruff, mypy, and schema JSON validation.** Expected: PASS.
- [ ] **Step 5: Add `docs/process/YYYY-MM-DD-config.md` and commit `feat: add project configuration loading`.**

## Task 2: Generic JUnit XML Inventory Reader

**Files:** Create `qcov/adapters/junit.py`, `tests/adapters/test_junit_adapter.py`; modify `qcov/adapters/__init__.py`.

**Interfaces:** Produces `InventoryRecord`, `ScanDiagnostic`, and `JUnitAdapter.scan(path) -> ScanResult`.

- [ ] **Step 1: Write failing tests for passed, failure, error, skipped, and malformed JUnit XML.**

```python
def test_junit_scan_maps_failure_without_creating_quality_evidence(tmp_path: Path) -> None:
    result = JUnitAdapter().scan(write_junit(tmp_path, '<failure/>'))
    assert result.records[0].status == "failed"
    assert not hasattr(result.records[0], "obligation")
```

- [ ] **Step 2: Run `pytest tests/adapters/test_junit_adapter.py -q`.** Expected: FAIL because the adapter is absent.
- [ ] **Step 3: Implement stdlib `xml.etree.ElementTree` parser and non-fatal `QCOV-SCAN-001` diagnostics.** Do not execute test commands or infer obligation IDs.
- [ ] **Step 4: Run adapter tests, Ruff, and mypy.** Expected: PASS.
- [ ] **Step 5: Record results and commit `feat: import JUnit XML test inventory`.**

## Task 3: coverage.py XML Inventory Reader

**Files:** Create `qcov/adapters/coverage.py`, `tests/adapters/test_coverage_adapter.py`; modify adapter exports.

**Interfaces:** Produces coverage inventory records with producer `coverage.py`, structural type, file identity, and line-rate metadata.

- [ ] **Step 1: Write failing tests for class/package line rates and malformed XML.**
- [ ] **Step 2: Run `pytest tests/adapters/test_coverage_adapter.py -q`.** Expected: FAIL.
- [ ] **Step 3: Implement the side-effect-free XML reader.** Preserve line-rate as metadata only; never represent it as a QCov score or proof.
- [ ] **Step 4: Run adapter checks.** Expected: PASS.
- [ ] **Step 5: Record results and commit `feat: import coverage XML inventory`.**

## Task 4: Discovery Service and `scan` Reports

**Files:** Create `qcov/engine/scan.py`, modify `qcov/engine/reports.py`, `qcov/cli/app.py`; create `tests/engine/test_scan.py`, modify `tests/cli/test_commands.py`.

**Interfaces:** Produces `scan_project(path, config_path) -> ScanReport`, `render_scan_json`, and `render_scan_markdown`.

- [ ] **Step 1: Write failing CLI tests.**

```python
def test_scan_json_lists_junit_file_and_record_count() -> None:
    result = runner.invoke(app, ["scan", "--config", str(CONFIG), "--format", "json"])
    assert result.exit_code == 0
    assert '"adapter": "junit"' in result.stdout
```

- [ ] **Step 2: Run scoped tests.** Expected: FAIL because scan has no config/report support.
- [ ] **Step 3: Implement aggregation of pytest, JUnit, and coverage findings.** Sort adapters/files/diagnostics; return 0 for inspectable projects and 4 for invalid configs.
- [ ] **Step 4: Run scan, CLI, Ruff, and mypy tests.** Expected: PASS.
- [ ] **Step 5: Record results and commit `feat: add config-driven evidence scan`.**

## Task 5: Config Defaults for Existing Gap Commands

**Files:** Modify `qcov/cli/app.py`; modify `tests/cli/test_commands.py`; create `examples/imported-reports/qcov.yaml` and fixtures.

**Interfaces:** `gaps`, `check`, and `report` accept `--config`; explicit `--obligation`/`--evidence` override defaults.

- [ ] **Step 1: Write a failing config-default command test.**

```python
def test_gaps_loads_paths_from_config() -> None:
    result = runner.invoke(app, ["gaps", "--config", str(CONFIG)])
    assert result.exit_code == 0
    assert "QO-REFUND-001" in result.stdout
```

- [ ] **Step 2: Run CLI test.** Expected: FAIL because `--config` is not accepted.
- [ ] **Step 3: Implement precedence and validated single-obligation behavior.** Empty/multiple obligation selections produce a stable configuration error rather than arbitrary aggregation.
- [ ] **Step 4: Run all CLI tests.** Expected: PASS.
- [ ] **Step 5: Record results and commit `feat: load gap inputs from project config`.**

## Task 6: Documentation, Example, and Release Verification

**Files:** Modify paired README and `docs/en|zh-CN/{requirements,architecture,protocol,technical-design,development,roadmap}.md`; create matching import-example READMEs, diagram update, ADR, docs tests, and final verification record.

- [ ] **Step 1: Write failing docs tests for `scan --format json`, config quickstart, paired references, and supported-format claims.**
- [ ] **Step 2: Run docs tests.** Expected: FAIL before docs are updated.
- [ ] **Step 3: Publish paired docs and runnable imported-reports fixture.** Clearly distinguish inventory imports from obligation evidence and unsupported future tools.
- [ ] **Step 4: Run `ruff check . && mypy qcov && pytest && python -m build && qcov scan --config examples/imported-reports/qcov.yaml && qcov scan --config examples/imported-reports/qcov.yaml --format json && git diff --check`.** Expected: all checks pass.
- [ ] **Step 5: Record executed results, commit `docs: document iteration 1 evidence import`, and inspect Git status.**
