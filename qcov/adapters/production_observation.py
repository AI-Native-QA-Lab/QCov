"""Strict local ProductionObservationReport inventory reader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from qcov.adapters.base import InventoryRecord, ScanDiagnostic, ScanResult
from qcov.models.protocol import ProductionObservationReport


class ProductionObservationAdapter:
    """Read offline production observations without inferring evidence."""

    name = "production-observation"

    def scan(self, path: Path) -> ScanResult:
        try:
            raw: Any = json.loads(path.read_text()) if path.suffix == ".json" else yaml.safe_load(path.read_text())
            report = ProductionObservationReport.model_validate(raw)
        except (OSError, json.JSONDecodeError, yaml.YAMLError, ValidationError) as error:
            return ScanResult(
                self.name, (), (ScanDiagnostic("QCOV-SCAN-001", str(error), str(path)),)
            )
        records = tuple(
            InventoryRecord(
                producer=self.name,
                identity=f"{report.metadata.id}::{observation.id}",
                status=observation.status,
                artifact_path=str(path),
                metadata={
                    **observation.attributes,
                    "category": observation.category,
                    "timestamp": observation.timestamp.isoformat(),
                },
            )
            for observation in report.observations
        )
        return ScanResult(self.name, records, ())
