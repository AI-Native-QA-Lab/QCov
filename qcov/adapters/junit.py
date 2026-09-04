"""Safe generic JUnit XML inventory reader."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from qcov.adapters.base import InventoryRecord, ScanDiagnostic, ScanResult


class JUnitAdapter:
    """Read testcase outcomes from JUnit XML without executing a test suite."""

    name = "junit"

    def scan(self, path: Path) -> ScanResult:
        try:
            root = ElementTree.parse(path).getroot()
        except (OSError, ElementTree.ParseError) as error:
            return ScanResult(
                self.name,
                (),
                (ScanDiagnostic("QCOV-SCAN-001", str(error), str(path)),),
            )
        records = tuple(self._record(case, path) for case in root.iter("testcase"))
        return ScanResult(self.name, records, ())

    def _record(self, case: ElementTree.Element, path: Path) -> InventoryRecord:
        classname = case.get("classname", "")
        name = case.get("name", "")
        status = "passed"
        if case.find("failure") is not None or case.find("error") is not None:
            status = "failed"
        elif case.find("skipped") is not None:
            status = "skipped"
        identity = f"{classname}::{name}" if classname else name
        return InventoryRecord(
            producer=self.name,
            identity=identity,
            status=status,
            artifact_path=str(path),
            metadata={"classname": classname, "name": name},
        )
