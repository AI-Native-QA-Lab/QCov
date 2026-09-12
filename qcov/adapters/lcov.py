"""LCOV tracefile inventory reader."""

from __future__ import annotations

from pathlib import Path

from qcov.adapters.base import InventoryRecord, ScanDiagnostic, ScanResult
from qcov.adapters.sdk import ADAPTER_PROTOCOL_VERSION


class LcovAdapter:
    name = "lcov"
    protocol_version = ADAPTER_PROTOCOL_VERSION

    def scan(self, path: Path) -> ScanResult:
        try:
            lines = path.read_text().splitlines()
        except OSError as error:
            return ScanResult(self.name, (), (ScanDiagnostic("QCOV-SCAN-001", str(error), str(path)),))
        records: list[InventoryRecord] = []
        source: str | None = None
        total = hits = 0
        diagnostics: list[ScanDiagnostic] = []
        for line in lines:
            if line.startswith("SF:"):
                if source is not None:
                    diagnostics.append(ScanDiagnostic("QCOV-SCAN-001", "Unterminated LCOV source section", str(path)))
                source, total, hits = line[3:], 0, 0
            elif line.startswith("DA:"):
                if source is None:
                    diagnostics.append(ScanDiagnostic("QCOV-SCAN-001", "LCOV DA record has no source", str(path)))
                    continue
                fields = line[3:].split(",")
                try:
                    int(fields[0]); count = int(fields[1])
                except (IndexError, ValueError):
                    diagnostics.append(ScanDiagnostic("QCOV-SCAN-001", "Invalid LCOV DA record", str(path)))
                    continue
                total += 1
                hits += count > 0
            elif line == "end_of_record":
                if source is None:
                    diagnostics.append(ScanDiagnostic("QCOV-SCAN-001", "LCOV record has no source", str(path)))
                else:
                    records.append(InventoryRecord(self.name, source, "observed", str(path), {"instrumentedLines": str(total), "hitLines": str(hits)}))
                    source = None
        if source is not None:
            diagnostics.append(ScanDiagnostic("QCOV-SCAN-001", "Unterminated LCOV source section", str(path)))
        return ScanResult(self.name, tuple(records), tuple(diagnostics))
