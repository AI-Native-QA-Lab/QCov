# Iteration 8 Production Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, offline production-observation inventory producer that can become evidence only through explicit mappings.

**Architecture:** A strict Pydantic report model is parsed by one built-in adapter into inventory records. Config discovery sends local report paths to that adapter; the existing mapping engine recognizes its status vocabulary and preserves the report observation timestamp when materializing evidence.

**Tech Stack:** Python 3.11+, Pydantic v2, PyYAML, Typer, pytest, Ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-09-11-iteration-8-production-evidence-design.md`

## Global Constraints

- Local files only; never execute project code or access a network service.
- `production-observation` is inventory only until an explicit `EvidenceMapping` matches it.
- Observation timestamp is the materialized production evidence timestamp; mapping timestamps cannot override it.
- Do not add automatic obligation/dimension inference, coverage promotion, external adapters, policy DSL, UI, persistence, or remote Git.
- Public docs stay paired English/Chinese; working docs and process records stay Chinese-only.

---

### Task 1: Strict production observation protocol and adapter

**Files:**
- Modify: `qcov/models/protocol.py`
- Create: `qcov/adapters/production_observation.py`
- Test: `tests/models/test_protocol.py`
- Test: `tests/adapters/test_production_observation_adapter.py`

**Consumes:** Existing `ProtocolModel`, `InventoryRecord`, `ScanResult` and `ScanDiagnostic`.

**Produces:** `ProductionObservationReport` and `ProductionObservationAdapter.scan(path) -> ScanResult`.

- [ ] **Step 1: Write failing model and adapter tests**

```python
def test_production_observation_adapter_retains_observation_identity_and_timestamp(tmp_path: Path) -> None:
    artifact = tmp_path / "production.yaml"
    artifact.write_text("""apiVersion: qcov.dev/v1alpha1
kind: ProductionObservationReport
metadata: {id: checkout-release}
observations:
  - id: availability
    category: runtime
    status: passed
    timestamp: 2026-09-11T00:00:00+08:00
    attributes: {service: checkout}
""")
    result = ProductionObservationAdapter().scan(artifact)
    assert result.records[0].identity == "checkout-release::availability"
    assert result.records[0].metadata["timestamp"] == "2026-09-11T00:00:00+08:00"

def test_production_observation_rejects_timezone_less_timestamp() -> None:
    with pytest.raises(ValueError):
        ProductionObservationReport.model_validate({...})
```

- [ ] **Step 2: Run focused tests and observe RED**

Run: `.venv/bin/pytest tests/models/test_protocol.py tests/adapters/test_production_observation_adapter.py -q`

Expected: import/attribute failure for the absent production model and adapter.

- [ ] **Step 3: Implement only the strict parser**

```python
class ProductionObservation(ProtocolModel):
    id: str = Field(min_length=1)
    category: Literal["runtime", "incident", "observability"]
    status: Literal["passed", "failed", "skipped", "unknown"]
    timestamp: datetime
    attributes: dict[str, str] = Field(default_factory=dict)

class ProductionObservationAdapter:
    name = "production-observation"
    def scan(self, path: Path) -> ScanResult: ...
```

Use YAML for non-`.json` paths, validate the whole report before creating any record, and return exactly one `QCOV-SCAN-001` diagnostic for load or validation failures.

- [ ] **Step 4: Re-run focused tests and observe GREEN**

Run: `.venv/bin/pytest tests/models/test_protocol.py tests/adapters/test_production_observation_adapter.py -q`

Expected: PASS.

### Task 2: Register and configure production inventory

**Files:**
- Modify: `qcov/adapters/registry.py`
- Modify: `qcov/models/config.py`
- Modify: `qcov/engine/scan.py`
- Test: `tests/adapters/test_registry.py`
- Test: `tests/models/test_config.py`
- Test: `tests/engine/test_scan.py`

**Consumes:** `ProductionObservationAdapter` from Task 1 and `ScanConfig` path conventions.

**Produces:** `scan.production`, `ResolvedPaths.production`, and production records in `scan_project`.

- [ ] **Step 1: Write failing config/discovery tests**

```python
def test_config_resolves_production_scan_paths(tmp_path: Path) -> None:
    ...
    assert paths.production == ((tmp_path / "reports/production.yaml").resolve(),)

def test_scan_project_collects_configured_production_inventory(tmp_path: Path) -> None:
    ...
    assert next(item for item in report.adapters if item.adapter == "production-observation").record_count == 1
```

- [ ] **Step 2: Run focused tests and observe RED**

Run: `.venv/bin/pytest tests/adapters/test_registry.py tests/models/test_config.py tests/engine/test_scan.py -q`

Expected: missing `production` resolved path / adapter summary.

- [ ] **Step 3: Add the config and registry wiring**

Add `production: list[str]` to `ScanConfig`, `production: tuple[Path, ...]` to `ResolvedPaths`, include `ProductionObservationAdapter()` in the fixed registry order, and map `production-observation` to `config.scan.production` in `scan_project`.

- [ ] **Step 4: Re-run focused tests and observe GREEN**

Run: `.venv/bin/pytest tests/adapters/test_registry.py tests/models/test_config.py tests/engine/test_scan.py -q`

Expected: PASS with deterministic sorted adapter names.

### Task 3: Explicit mapping and timestamp authority

**Files:**
- Modify: `qcov/models/protocol.py`
- Modify: `qcov/engine/mapping.py`
- Test: `tests/engine/test_mapping.py`

**Consumes:** production inventory records from Task 1.

**Produces:** explicitly mapped production `QualityEvidence` with retained observation timestamp.

- [ ] **Step 1: Write failing mapping tests**

```python
def test_apply_mappings_materializes_explicit_production_observation_timestamp(tmp_path: Path) -> None:
    result = apply_mappings([InventoryRecord(
        "production-observation", "checkout-release::availability", "passed",
        str(tmp_path / "production.yaml"), {"timestamp": "2026-09-11T00:00:00+08:00"}
    )], [production_mapping], tmp_path)
    assert result.evidence[0].execution.status == "passed"
    assert result.evidence[0].execution.timestamp.isoformat() == "2026-09-11T00:00:00+08:00"
```

Also assert failed stays failed and a production record without a matching map creates no evidence.

- [ ] **Step 2: Run mapping tests and observe RED**

Run: `.venv/bin/pytest tests/engine/test_mapping.py -q`

Expected: protocol rejects the producer or materialized timestamp equals mapping default.

- [ ] **Step 3: Implement the smallest mapping extension**

Extend `MappingSource.producer`; use a dedicated production status map and parse the adapter-guaranteed `record.metadata["timestamp"]` for that producer before constructing `QualityEvidence`. Keep existing JUnit and Playwright timestamp behavior unchanged.

- [ ] **Step 4: Re-run mapping tests and observe GREEN**

Run: `.venv/bin/pytest tests/engine/test_mapping.py -q`

Expected: PASS.

### Task 4: End-to-end CLI contract and examples

**Files:**
- Create: `examples/production-observations/production.yaml`
- Create: `examples/production-observations/mapping.yaml`
- Create: `examples/production-observations/qcov.yaml`
- Modify: `tests/cli/test_map.py`
- Modify: `tests/cli/test_commands.py`

**Consumes:** Tasks 1–3.

**Produces:** a runnable local example showing scan, map preview and the un-mapped boundary.

- [ ] **Step 1: Write failing CLI tests**

```python
def test_map_preview_materializes_explicit_production_observation(tmp_path: Path) -> None:
    result = runner.invoke(app, ["map", "preview", "--config", str(config), "--format", "json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["evidence"][0]["producer"] == "production-observation"

def test_unmapped_production_inventory_does_not_change_gap(tmp_path: Path) -> None:
    ...
    assert "COVERED" not in result.stdout
```

- [ ] **Step 2: Run focused CLI tests and observe RED**

Run: `.venv/bin/pytest tests/cli/test_map.py tests/cli/test_commands.py -q`

Expected: production fixtures are not recognized before Tasks 1–3 are complete.

- [ ] **Step 3: Add only static example artifacts and adjust existing command expectations**

Do not add a command or network integration. Use the existing `scan`, `map preview`, `gaps`, and `policy check` commands.

- [ ] **Step 4: Re-run focused CLI tests and observe GREEN**

Run: `.venv/bin/pytest tests/cli/test_map.py tests/cli/test_commands.py -q`

Expected: PASS.

### Task 5: Documentation, process record, and release-facing version state

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/en/roadmap.md`
- Modify: `docs/zh-CN/roadmap.md`
- Modify: `docs/en/requirements.md`
- Modify: `docs/zh-CN/requirements.md`
- Create: `docs/en/production-evidence.md`
- Create: `docs/zh-CN/production-evidence.md`
- Create: `docs/process/2026-09-11-iteration-8-production-evidence.md`
- Modify: `tests/docs/test_documentation_links.py`

**Consumes:** example commands from Task 4 and actual executed test results.

**Produces:** bilingual public explanation, Chinese-only execution evidence, and a roadmap that marks Iteration 8 as the production-observation foundation before QCov 1.0 / Iteration 9.

- [ ] **Step 1: Write failing documentation link tests**

Add assertions that both production evidence pages are linked by their language README and every newly added relative link resolves.

- [ ] **Step 2: Run documentation test and observe RED**

Run: `.venv/bin/pytest tests/docs/test_documentation_links.py -q`

Expected: missing pages or missing links.

- [ ] **Step 3: Write concise paired public docs and Chinese process record**

Document report schema, local-only boundary, explicit mapping requirement, observation timestamp authority, commands, and the fact that a passed observation is not coverage without mapping. Update roadmap / requirements to show Iteration 8 delivered as the production-observation foundation and QCov 1.0 / Iteration 9 as the next delivery track. Record only executed RED/GREEN and final verification results in the process document.

- [ ] **Step 4: Re-run documentation test and observe GREEN**

Run: `.venv/bin/pytest tests/docs/test_documentation_links.py -q`

Expected: PASS.

### Task 6: Full verification and delivery review

**Files:** all touched files above.

- [ ] **Step 1: Run full tests**

Run: `.venv/bin/pytest -q`

Expected: PASS.

- [ ] **Step 2: Run static and packaging gates**

Run: `.venv/bin/ruff check . && .venv/bin/mypy qcov && .venv/bin/python -m build && git diff --check`

Expected: all commands succeed.

- [ ] **Step 3: Inspect final scope**

Run: `git status --short && git diff --stat`

Expected: only Iteration 8 code, tests, examples, docs, and process records are changed.
