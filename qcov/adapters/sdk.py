"""Public in-process contract for inventory-only adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from qcov.adapters.base import ScanDiagnostic, ScanResult

ADAPTER_PROTOCOL_VERSION = "qcov.adapter/v1"

__all__ = ["ADAPTER_PROTOCOL_VERSION", "InventoryAdapter", "ScanDiagnostic", "ScanResult"]


@runtime_checkable
class InventoryAdapter(Protocol):
    """A side-effect-free persisted-artifact inventory reader."""

    name: str
    protocol_version: str

    def scan(self, path: Path) -> ScanResult: ...
