"""Playwright JSON reporter inventory reader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qcov.adapters.base import InventoryRecord, ScanDiagnostic, ScanResult
from qcov.adapters.sdk import ADAPTER_PROTOCOL_VERSION


class PlaywrightAdapter:
    name = "playwright"
    protocol_version = ADAPTER_PROTOCOL_VERSION

    def scan(self, path: Path) -> ScanResult:
        try:
            document: Any = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            return ScanResult(self.name, (), (ScanDiagnostic("QCOV-SCAN-001", str(error), str(path)),))
        records: list[InventoryRecord] = []
        for suite in document.get("suites", []) if isinstance(document, dict) else []:
            self._collect_suite(suite, (), records, path)
        return ScanResult(self.name, tuple(records), ())

    def _collect_suite(
        self, suite: Any, parents: tuple[str, ...], records: list[InventoryRecord], path: Path
    ) -> None:
        if not isinstance(suite, dict):
            return
        title = str(suite.get("title", ""))
        current = (*parents, title) if title else parents
        file_name = str(suite.get("file", ""))
        for spec in suite.get("specs", []):
            if not isinstance(spec, dict):
                continue
            spec_title = str(spec.get("title", ""))
            for test in spec.get("tests", []):
                if not isinstance(test, dict):
                    continue
                project = str(test.get("projectName", ""))
                status = str(test.get("status", "skipped"))
                if status == "expected":
                    status = "passed"
                identity = " > ".join((*current, spec_title))
                if project:
                    identity += f" [{project}]"
                records.append(
                    InventoryRecord(self.name, f"{file_name}::{identity}", status, str(path), {"file": file_name, "project": project})
                )
        for child in suite.get("suites", []):
            self._collect_suite(child, current, records, path)
