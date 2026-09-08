from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from qcov.cli.app import app

runner = CliRunner()


def _write_project(tmp_path: Path) -> Path:
    (tmp_path / "obligation.yaml").write_text(Path("examples/refund/obligation.yaml").read_text())
    (tmp_path / "evidence").mkdir()
    # only behavior covered → other dimensions remain gaps
    (tmp_path / "evidence" / "behavior.yaml").write_text(
        Path("examples/refund/evidence/behavior.yaml").read_text()
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\n"
        "kind: QCovConfig\n"
        "obligations: [obligation.yaml]\n"
        "evidence: [evidence/*.yaml]\n"
    )
    return config


def test_plan_writes_quality_plan_from_config(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    output = tmp_path / "plan.yaml"
    result = runner.invoke(
        app,
        ["plan", "--config", str(config), "--output", str(output), "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["proposal"]["type"] == "quality_plan"
    assert payload["source"]["kind"] == "evaluation_gaps"
    assert payload["items"], "expected unproven dimensions"
    assert payload["items"][0]["detail"]["rank"] == 1
    written = yaml.safe_load(output.read_text())
    assert written["kind"] == "QualityProposal"
    assert written["proposal"]["type"] == "quality_plan"


def test_plan_rejects_config_with_direct_inputs(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    result = runner.invoke(
        app,
        [
            "plan",
            "--config",
            str(config),
            "--obligation",
            str(tmp_path / "obligation.yaml"),
            "--evidence",
            str(tmp_path / "evidence" / "behavior.yaml"),
        ],
    )
    assert result.exit_code == 4
    assert "QCOV-CLI-003" in result.output


def test_plan_empty_when_fully_covered(tmp_path: Path) -> None:
    obl = tmp_path / "obligation.yaml"
    obl.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: TestingObligation
metadata:
  id: QO-ONE
  title: {en: One, zh-CN: 一}
source: {type: requirement, ref: R1}
risk: {domain: x, severity: low}
requiredEvidence:
  behavior: [api_test]
"""
    )
    ev = tmp_path / "evidence.yaml"
    ev.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityEvidence
metadata: {id: QE-1}
obligation: {ref: QO-ONE}
evidence: {dimension: behavior, type: api_test}
producer: {name: pytest, adapter: qcov-pytest}
execution:
  status: passed
  timestamp: "2026-09-08T12:00:00+08:00"
artifact: {path: tests/example.py}
confidence: {deterministic: true, reproducible: true}
"""
    )
    result = runner.invoke(
        app,
        [
            "plan",
            "--obligation",
            str(obl),
            "--evidence",
            str(ev),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["items"] == []


def test_gaps_unaffected_by_plan_yaml(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    before = runner.invoke(app, ["gaps", "--config", str(config), "--format", "json"])
    assert before.exit_code == 0, before.output

    plan_in_evidence = tmp_path / "evidence" / "plan.yaml"
    plan_in_evidence.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityProposal
metadata:
  id: QP-plan-ignore
  createdAt: 2026-09-08T12:00:00+08:00
proposal:
  type: quality_plan
  status: draft
source:
  kind: evaluation_gaps
  refs: []
provider:
  name: offline
items: []
"""
    )
    after = runner.invoke(app, ["gaps", "--config", str(config), "--format", "json"])
    # Proposal in evidence glob must not be treated as QualityEvidence
    assert after.exit_code == 4
    assert "QCOV-SCHEMA-001" in after.output
    assert json.loads(before.output)["results"]
