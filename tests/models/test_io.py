from __future__ import annotations

from pathlib import Path

import pytest

from qcov.models.io import ProtocolLoadError, load_evidence


def test_load_evidence_reports_schema_error_with_stable_code(tmp_path: Path) -> None:
    invalid = tmp_path / "evidence.yaml"
    invalid.write_text("kind: QualityEvidence\n")

    with pytest.raises(ProtocolLoadError, match="QCOV-SCHEMA-001"):
        load_evidence(invalid)
