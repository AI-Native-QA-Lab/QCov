# QCov Iteration 2 Cross-Language Adapters Implementation Plan

> **For agentic workers:** Execute task-by-task with focused RED/GREEN tests and record the observed commands.

**Goal:** Discover Playwright JSON and LCOV inventory from QCov configuration through a deterministic built-in registry.

**Architecture:** Report readers implement `InventoryScanner`; `qcov.adapters.registry` maps stable names to readers; `scan_project` resolves configured paths and aggregates their results. Inventory stays outside the Gap Engine.

**Tech Stack:** Python 3.11+, stdlib `json`, pathlib, Pydantic v2, Typer, pytest, Ruff, mypy.

---

### Task 1: Adapter registry and configuration

**Files:** Create `qcov/adapters/registry.py`, `tests/adapters/test_registry.py`; modify `qcov/models/config.py`, `qcov/engine/scan.py`, `tests/models/test_config.py`, `tests/engine/test_scan.py`, and generated `schemas/config.schema.json`.

- [x] Write focused tests for deterministic registry order and `scan.playwright`/`scan.lcov` relative paths.
- [x] Run their scoped tests and observe RED because the readers/config fields do not exist.
- [x] Add the two config lists and an explicit built-in registry; replace report-reader hard-coding while retaining pytest source discovery.
- [x] Re-run scoped tests for GREEN and record the output.

### Task 2: Playwright JSON inventory

**Files:** Create `qcov/adapters/playwright.py`, `tests/adapters/test_playwright_adapter.py`.

- [x] Write tests for nested suites, statuses, project names, and malformed JSON diagnostics.
- [x] Run the adapter test and observe RED because `PlaywrightAdapter` does not exist.
- [x] Parse Playwright JSON reporter shape using stdlib JSON and recursively collect specs; return `QCOV-SCAN-001` for unreadable JSON.
- [x] Re-run the adapter test for GREEN and record the output.

### Task 3: LCOV inventory

**Files:** Create `qcov/adapters/lcov.py`, `tests/adapters/test_lcov_adapter.py`.

- [x] Write tests for line-count aggregation, optional DA checksum, multiple source files, and invalid source sections.
- [x] Run the adapter test and observe RED because `LcovAdapter` does not exist.
- [x] Implement a line-oriented, side-effect-free parser producing per-source inventory records and diagnostics.
- [x] Re-run the adapter test for GREEN and record the output.

### Task 4: User documentation, examples, and release verification

**Files:** Create fixtures under `examples/imported-reports/`; modify `examples/imported-reports/qcov.yaml`, both example READMEs, paired root READMEs, paired technical-design/development/roadmap docs, docs tests, and `docs/process/2026-09-06-iteration-2-verification.md`.

- [ ] Write docs/CLI tests for both new adapter names and record their RED result. (The assertion now exists, but its RED result cannot be reconstructed after the documentation change.)
- [x] Add a runnable configuration and fixtures plus matching English/Chinese documentation explaining that imports are inventory only.
- [x] Run focused tests, full test suite, Ruff, mypy, build, example scans, and `git diff --check`; write exact results in the process record.
