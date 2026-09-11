"""Collect inventory records needed for explicit evidence mapping."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from qcov.adapters.base import InventoryRecord, ScanDiagnostic
from qcov.adapters.junit import JUnitAdapter
from qcov.adapters.playwright import PlaywrightAdapter
from qcov.adapters.production_observation import ProductionObservationAdapter
from qcov.engine.scan import scan_adapter_files
from qcov.models.config import ResolvedPaths


@dataclass(frozen=True)
class InventoryCollection:
    records: tuple[InventoryRecord, ...]
    diagnostics: tuple[ScanDiagnostic, ...]


def collect_mappable_inventory(resolved: ResolvedPaths) -> InventoryCollection:
    """Scan configured explicitly mappable artifacts and retain records."""
    records: list[InventoryRecord] = []
    diagnostics: list[ScanDiagnostic] = []
    for adapter, paths in (
        (JUnitAdapter(), resolved.junit),
        (PlaywrightAdapter(), resolved.playwright),
        (ProductionObservationAdapter(), resolved.production),
    ):
        _summary, adapter_records, adapter_diagnostics = scan_adapter_files(adapter, paths)
        records.extend(adapter_records)
        diagnostics.extend(adapter_diagnostics)
    diagnostics.sort(key=lambda item: (item.code, item.message, item.artifact_path))
    return InventoryCollection(tuple(records), tuple(diagnostics))


def config_dir_for(config_path: Path) -> Path:
    return config_path.resolve().parent
