from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from qcov.cli.app import app

runner = CliRunner()


def _write_marker_only_project(tmp_path: Path) -> Path:
    (tmp_path / "obligation.yaml").write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: TestingObligation
metadata:
  id: QO-REFUND-001
  title:
    en: Refund marker wiring
    zh-CN: 退款 marker 接线
source:
  type: requirement
  ref: REFUND-001
risk:
  domain: financial
  severity: critical
requiredEvidence:
  behavior: [pytest_marker]
"""
    )
    (tmp_path / "test_refund.py").write_text(
        'import pytest\n\n@pytest.mark.qcov("QO-REFUND-001")\ndef test_refund():\n    pass\n'
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\n"
        "kind: QCovConfig\n"
        "obligations: [obligation.yaml]\n"
        "evidence: []\n"
    )
    return config


def test_gaps_config_includes_pytest_marker_evidence_as_unknown(tmp_path: Path) -> None:
    config = _write_marker_only_project(tmp_path)
    result = runner.invoke(app, ["gaps", "--config", str(config), "--format", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    behavior = next(item for item in payload["results"][0]["dimensions"] if item["dimension"] == "behavior")
    assert behavior["status"] == "UNKNOWN"
    assert "QE-PYTEST-QO-REFUND-001-test_refund" in behavior["observedEvidenceIds"]
    assert payload["results"][0]["status"] != "COVERED"
