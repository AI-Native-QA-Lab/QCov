"""Config-driven, local-only evidence artifact discovery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from qcov.adapters.base import InventoryScanner, ScanDiagnostic
from qcov.adapters.pytest import PytestAdapter
from qcov.adapters.registry import inventory_adapters
from qcov.models.config import resolve_patterns
from qcov.models.io import load_config


@dataclass(frozen=True)
class AdapterScanSummary:
    """Stable aggregate facts about one producer scan."""

    adapter: str
    detected: bool
    files: tuple[str, ...]
    record_count: int


@dataclass(frozen=True)
class ScanReport:
    """Local artifact discovery result for presentation layers."""

    adapters: tuple[AdapterScanSummary, ...]
    diagnostics: tuple[ScanDiagnostic, ...]


def _scan_files(adapter: InventoryScanner, paths: tuple[Path, ...]) -> tuple[AdapterScanSummary, tuple[ScanDiagnostic, ...]]:
    records = 0
    diagnostics: list[ScanDiagnostic] = []
    files: list[str] = []
    for path in paths:
        if not path.exists():
            diagnostics.append(ScanDiagnostic("QCOV-SCAN-001", "Configured artifact does not exist", str(path)))
            continue
        result = adapter.scan(path)
        files.append(str(path))
        records += len(result.records)
        diagnostics.extend(result.diagnostics)
    return AdapterScanSummary(adapter.name, bool(files), tuple(files), records), tuple(diagnostics)


def scan_project(project_path: Path, config_path: Path) -> ScanReport:
    """Discover supported local inputs without executing project code."""
    config = load_config(config_path)
    pytest_adapter = PytestAdapter()
    pytest = pytest_adapter.detect(project_path)
    pytest_files = tuple(str(path) for path in pytest_adapter.test_files(project_path))
    pytest_summary = AdapterScanSummary(
        pytest.name, pytest.detected, pytest_files, len(pytest_adapter.collect(project_path))
    )
    configured = {
        "junit": config.scan.junit,
        "coverage.py": config.scan.coverage,
        "lcov": config.scan.lcov,
        "playwright": config.scan.playwright,
    }
    summaries: list[AdapterScanSummary] = [pytest_summary]
    diagnostics: list[ScanDiagnostic] = []
    for adapter in inventory_adapters():
        summary, adapter_diagnostics = _scan_files(
            adapter, resolve_patterns(configured[adapter.name], config_path.resolve().parent, include_missing=True)
        )
        summaries.append(summary)
        diagnostics.extend(adapter_diagnostics)
    return ScanReport(
        adapters=tuple(sorted(summaries, key=lambda item: item.adapter)),
        diagnostics=tuple(sorted(diagnostics, key=lambda item: item.artifact_path)),
    )
