from __future__ import annotations

import json
from pathlib import Path

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


def test_agent_next_from_config_matches_plan(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan = runner.invoke(app, ["plan", "--config", str(config), "--format", "json"])
    assert plan.exit_code == 0, plan.output
    nxt = runner.invoke(
        app, ["agent", "next", "--config", str(config), "--format", "json"]
    )
    assert nxt.exit_code == 0, nxt.output
    plan_id = json.loads(plan.output)["items"][0]["id"]
    body = json.loads(nxt.output)
    assert body["contractVersion"] == "qcov.agent/v1"
    assert body["command"] == "agent.next"
    assert body["payload"]["source"] == "evaluation"
    assert body["payload"]["items"][0]["id"] == plan_id


def test_agent_next_from_plan_file(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan_path = tmp_path / "plan.yaml"
    wrote = runner.invoke(app, ["plan", "--config", str(config), "--output", str(plan_path)])
    assert wrote.exit_code == 0, wrote.output
    nxt = runner.invoke(
        app, ["agent", "next", "--plan", str(plan_path), "--format", "json"]
    )
    assert nxt.exit_code == 0, nxt.output
    assert json.loads(nxt.output)["payload"]["source"] == "plan_file"


def test_agent_next_rejects_plan_with_config(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan_path = tmp_path / "plan.yaml"
    wrote = runner.invoke(app, ["plan", "--config", str(config), "--output", str(plan_path)])
    assert wrote.exit_code == 0, wrote.output
    result = runner.invoke(
        app,
        ["agent", "next", "--plan", str(plan_path), "--config", str(config)],
    )
    assert result.exit_code == 4
    assert "QCOV-CLI-006" in result.output


def test_agent_validate_evidence_valid_for_load(tmp_path: Path) -> None:
    ev = tmp_path / "behavior.yaml"
    ev.write_text(Path("examples/refund/evidence/behavior.yaml").read_text())
    result = runner.invoke(
        app, ["agent", "validate-evidence", "--evidence", str(ev), "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["command"] == "agent.validate_evidence"
    assert body["payload"]["allValidForLoad"] is True
    assert "COVERED" not in result.output
    assert "PASS" not in result.output
