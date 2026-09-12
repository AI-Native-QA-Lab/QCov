"""JaCoCo XML inventory reader."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from qcov.adapters.base import InventoryRecord, ScanDiagnostic, ScanResult
from qcov.adapters.sdk import ADAPTER_PROTOCOL_VERSION


class JacocoAdapter:
    """Read JaCoCo classes and methods without producing Quality Evidence."""

    name = "jacoco"
    protocol_version = ADAPTER_PROTOCOL_VERSION

    def scan(self, path: Path) -> ScanResult:
        try:
            root = ElementTree.parse(path).getroot()
        except (OSError, ElementTree.ParseError) as error:
            return ScanResult(self.name, (), (ScanDiagnostic("QCOV-SCAN-001", str(error), str(path)),))
        records: list[InventoryRecord] = []
        for package in root.iter("package"):
            package_name = package.get("name", "").replace("/", ".")
            for class_node in package.findall("class"):
                identity = class_node.get("name", "").replace("/", ".") or package_name
                methods = class_node.findall("method")
                if not methods:
                    records.append(self._record(identity, path, {}))
                    continue
                for method in methods:
                    method_name = method.get("name", "")
                    descriptor = method.get("desc", "")
                    records.append(self._record(f"{identity}::{method_name}{descriptor}", path, {"class": identity, "method": method_name, "descriptor": descriptor}))
        return ScanResult(self.name, tuple(records), ())

    def _record(self, identity: str, path: Path, metadata: dict[str, str]) -> InventoryRecord:
        return InventoryRecord(self.name, identity, "unknown", str(path), metadata)
