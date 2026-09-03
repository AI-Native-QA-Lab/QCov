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


class Adapter(Protocol):
    name: str

    def detect(self, project_path: Path) -> DetectionResult: ...

    def collect(self, project_path: Path) -> list[QualityEvidence]: ...
