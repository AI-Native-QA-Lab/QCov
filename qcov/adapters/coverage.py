"""Safe coverage.py XML inventory reader."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from qcov.adapters.base import InventoryRecord, ScanDiagnostic, ScanResult
from qcov.adapters.sdk import ADAPTER_PROTOCOL_VERSION


class CoverageAdapter:
    """Read structural coverage observations without producing quality scores."""

    name = "coverage.py"
    protocol_version = ADAPTER_PROTOCOL_VERSION

    def scan(self, path: Path) -> ScanResult:
        try:
            root = ElementTree.parse(path).getroot()
        except (OSError, ElementTree.ParseError) as error:
            return ScanResult(
                self.name,
                (),
                (ScanDiagnostic("QCOV-SCAN-001", str(error), str(path)),),
            )
        records = tuple(self._record(item, path) for item in root.iter("class"))
        return ScanResult(self.name, records, ())

    def _record(self, item: ElementTree.Element, path: Path) -> InventoryRecord:
        return InventoryRecord(
            producer=self.name,
            identity=item.get("filename", item.get("name", "")),
            status="observed",
            artifact_path=str(path),
            metadata={
                "lineRate": item.get("line-rate", ""),
                "className": item.get("name", ""),
            },
        )
