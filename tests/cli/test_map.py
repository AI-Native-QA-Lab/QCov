from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from qcov.cli.app import app

runner = CliRunner()


def _write_mapping_project(tmp_path: Path) -> Path:
    obligation = tmp_path / "obligation.yaml"
    obligation.write_text(Path("examples/refund/obligation.yaml").read_text())
    mapping_dir = tmp_path / "mappings"
    mapping_dir.mkdir()
    (mapping_dir / "refund.yaml").write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: EvidenceMapping
metadata:
  id: refund-import-mapping
defaultTimestamp: "2026-09-08T00:00:00+08:00"
mappings:
  - from:
      producer: junit
      identity: "refund.api::refund_is_accepted"
    to:
      obligationRef: QO-REFUND-001
      dimension: behavior
      type: api_test
"""
    )
    (tmp_path / "junit.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="refund" tests="1">
  <testcase classname="refund.api" name="refund_is_accepted" />
</testsuite>
"""
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\n"
        "kind: QCovConfig\n"
        "obligations: [obligation.yaml]\n"
        "evidence: []\n"
        "mapping: [mappings/*.yaml]\n"
        "scan:\n  junit: [junit.xml]\n"
    )
    return config


def test_map_preview_json_lists_mapped_evidence(tmp_path: Path) -> None:
    config = _write_mapping_project(tmp_path)
    result = runner.invoke(app, ["map", "preview", "--config", str(config), "--format", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mappingIds"] == ["refund-import-mapping"]
    assert payload["evidence"][0]["obligationRef"] == "QO-REFUND-001"
    assert payload["evidence"][0]["executionStatus"] == "passed"
    assert payload["evidence"][0]["artifactPath"] == "junit.xml"


def test_map_preview_materializes_explicit_production_observation(tmp_path: Path) -> None:
    (tmp_path / "production.yaml").write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: ProductionObservationReport
metadata: {id: release}
observations:
  - id: monitor
    category: observability
    status: passed
    timestamp: 2026-09-11T00:00:00+08:00
"""
    )
    (tmp_path / "mapping.yaml").write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: EvidenceMapping
metadata: {id: production}
defaultTimestamp: 2026-09-10T00:00:00+08:00
mappings:
  - from: {producer: production-observation, identity: release::monitor}
    to: {obligationRef: QO-REFUND-001, dimension: production, type: runtime_monitor}
"""
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        "mapping: [mapping.yaml]\nscan:\n  production: [production.yaml]\n"
    )

    result = runner.invoke(app, ["map", "preview", "--config", str(config), "--format", "json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["evidence"][0]["producer"] == "production-observation"
    assert payload["evidence"][0]["executionStatus"] == "passed"


def test_gaps_config_merges_mapped_evidence(tmp_path: Path) -> None:
    config = _write_mapping_project(tmp_path)
    result = runner.invoke(app, ["gaps", "--config", str(config), "--format", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "mappingDiagnostics" in payload
    behavior = next(item for item in payload["results"][0]["dimensions"] if item["dimension"] == "behavior")
    assert behavior["status"] == "COVERED"
    assert any(item.startswith("QE-MAP-") for item in behavior["observedEvidenceIds"])


def test_map_preview_zh_cn_title(tmp_path: Path) -> None:
    config = _write_mapping_project(tmp_path)
    result = runner.invoke(
        app, ["map", "preview", "--config", str(config), "--locale", "zh-CN"]
    )
    assert result.exit_code == 0
    assert "证据映射预览" in result.output


def test_gaps_without_mapping_omits_mapping_diagnostics(tmp_path: Path) -> None:
    obligation = tmp_path / "obligation.yaml"
    evidence = tmp_path / "evidence.yaml"
    obligation.write_text(Path("examples/refund/obligation.yaml").read_text())
    evidence.write_text(Path("examples/refund/evidence/behavior.yaml").read_text())
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        "obligations: [obligation.yaml]\nevidence: [evidence.yaml]\n"
    )
    result = runner.invoke(app, ["gaps", "--config", str(config), "--format", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "mappingDiagnostics" not in payload


def test_direct_obligation_evidence_paths_do_not_apply_mapping(tmp_path: Path) -> None:
    config = _write_mapping_project(tmp_path)
    evidence = tmp_path / "hand.yaml"
    evidence.write_text(Path("examples/refund/evidence/behavior.yaml").read_text())
    result = runner.invoke(
        app,
        [
            "gaps",
            "--obligation",
            str(tmp_path / "obligation.yaml"),
            "--evidence",
            str(evidence),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "mappingDiagnostics" not in payload
    behavior = next(item for item in payload["results"][0]["dimensions"] if item["dimension"] == "behavior")
    assert behavior["observedEvidenceIds"] == ["QE-REFUND-BEHAVIOR-001"]
    assert config.exists()


def test_policy_check_includes_mapping_diagnostics(tmp_path: Path) -> None:
    config = _write_mapping_project(tmp_path)
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityPolicy
metadata:
  id: gate
rules:
  default:
    allowedStatuses: [COVERED, PARTIAL, MISSING, UNKNOWN]
waivers: []
"""
    )
    result = runner.invoke(
        app,
        [
            "policy",
            "check",
            "--config",
            str(config),
            "--policy",
            str(policy),
            "--as-of",
            "2026-09-08T00:00:00+08:00",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "mappingDiagnostics" in payload


def test_gaps_markdown_includes_mapping_diagnostics_section_when_empty(tmp_path: Path) -> None:
    config = _write_mapping_project(tmp_path)
    result = runner.invoke(app, ["gaps", "--config", str(config), "--locale", "en"])
    assert result.exit_code == 0, result.output
    assert "Mapping diagnostics" in result.output
