"""Minimal built-in adapter contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from qcov.models.protocol import QualityEvidence


@dataclass(frozen=True)
class DetectionResult:
    name: str
    detected: bool
    detail: str


@dataclass(frozen=True)
class InventoryRecord:
    """An imported observation with no inferred obligation relationship."""

    producer: str
    identity: str
    status: str
    artifact_path: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class ScanDiagnostic:
    """A non-fatal local artifact inspection diagnostic."""

    code: str
    message: str
    artifact_path: str


@dataclass(frozen=True)
class ScanResult:
    """Inventory records and diagnostics from one side-effect-free scan."""

    adapter: str
    records: tuple[InventoryRecord, ...]
    diagnostics: tuple[ScanDiagnostic, ...]


class Adapter(Protocol):
    name: str

    def detect(self, project_path: Path) -> DetectionResult: ...

    def collect(self, project_path: Path) -> list[QualityEvidence]: ...


class InventoryScanner(Protocol):
    """Protocol for adapters that inspect a persisted artifact as inventory."""

    name: str

    def scan(self, path: Path) -> ScanResult: ...
