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


def test_explain_gap_json_has_contract_version(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    result = runner.invoke(
        app,
        [
            "explain",
            "--config",
            str(config),
            "--obligation-id",
            "QO-REFUND-001",
            "--dimension",
            "boundary",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["contractVersion"] == "qcov.agent/v1"
    assert payload["command"] == "explain"
    assert payload["payload"]["mode"] == "gap"
    assert payload["payload"]["reasons"]


def test_explain_plan_item(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan_path = tmp_path / "plan.yaml"
    plan_result = runner.invoke(
        app, ["plan", "--config", str(config), "--output", str(plan_path)]
    )
    assert plan_result.exit_code == 0, plan_result.output
    plan = yaml.safe_load(plan_path.read_text())
    item_id = plan["items"][0]["id"]
    result = runner.invoke(
        app,
        ["explain", "--plan", str(plan_path), "--item-id", item_id, "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["payload"]["mode"] == "plan_item"
    assert body["payload"]["itemId"] == item_id


def test_explain_evidence_mode(tmp_path: Path) -> None:
    obl = tmp_path / "obligation.yaml"
    obl.write_text(Path("examples/refund/obligation.yaml").read_text())
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        Path("examples/refund/evidence/behavior.yaml")
        .read_text()
        .replace("QO-REFUND-001", "QO-OTHER")
    )
    result = runner.invoke(
        app,
        [
            "explain",
            "--obligation",
            str(obl),
            "--evidence",
            str(bad),
            "--obligation-id",
            "QO-REFUND-001",
            "--dimension",
            "behavior",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    codes = {r["code"] for r in json.loads(result.output)["payload"]["reasons"]}
    assert "OBLIGATION_REF_MISMATCH" in codes


def test_explain_rejects_config_with_direct_inputs(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    result = runner.invoke(
        app,
        [
            "explain",
            "--config",
            str(config),
            "--obligation",
            str(tmp_path / "obligation.yaml"),
            "--evidence",
            str(tmp_path / "evidence" / "behavior.yaml"),
            "--obligation-id",
            "QO-REFUND-001",
            "--dimension",
            "boundary",
        ],
    )
    assert result.exit_code == 4
    assert "QCOV-CLI-003" in result.output


def test_explain_unknown_dimension(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    result = runner.invoke(
        app,
        [
            "explain",
            "--config",
            str(config),
            "--obligation-id",
            "QO-REFUND-001",
            "--dimension",
            "not-a-dimension",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 4
    assert "QCOV-AGENT-002" in result.output
