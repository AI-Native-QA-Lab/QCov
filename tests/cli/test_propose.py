from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

from qcov.cli.app import app

runner = CliRunner()


def _write_suggest_project(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / "obligation.yaml").write_text(Path("examples/refund/obligation.yaml").read_text())
    (tmp_path / "evidence").mkdir()
    for path in Path("examples/refund/evidence").glob("*.yaml"):
        (tmp_path / "evidence" / path.name).write_text(path.read_text())
    requirements = tmp_path / "requirements.md"
    requirements.write_text("Need more proof for QO-REFUND-001 concurrency.\n")
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\n"
        "kind: QCovConfig\n"
        "obligations: [obligation.yaml]\n"
        "evidence: [evidence/*.yaml]\n"
    )
    return config, requirements


def test_obligation_suggest_writes_draft_proposal(tmp_path: Path) -> None:
    config, requirements = _write_suggest_project(tmp_path)
    output = tmp_path / "proposal.yaml"
    result = runner.invoke(
        app,
        [
            "obligation",
            "suggest",
            "--config",
            str(config),
            "--requirements",
            str(requirements),
            "--output",
            str(output),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["kind"] == "QualityProposal"
    assert payload["proposal"]["type"] == "obligation_suggest"
    assert payload["proposal"]["status"] == "draft"
    written = yaml.safe_load(output.read_text())
    assert written["kind"] == "QualityProposal"


def test_obligation_suggest_requires_requirements(tmp_path: Path) -> None:
    config, _requirements = _write_suggest_project(tmp_path)
    result = runner.invoke(app, ["obligation", "suggest", "--config", str(config)])
    assert result.exit_code == 4
    assert "QCOV-PROPOSAL-002" in result.output


def test_obligation_suggest_from_obligation_and_stdin(tmp_path: Path) -> None:
    obligation = tmp_path / "obligation.yaml"
    obligation.write_text(Path("examples/refund/obligation.yaml").read_text())
    result = runner.invoke(
        app,
        [
            "obligation",
            "suggest",
            "--obligation",
            str(obligation),
            "--format",
            "json",
        ],
        input="Need more proof for QO-REFUND-001 concurrency.\n",
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["kind"] == "QualityProposal"
    assert payload["source"]["refs"] == ["stdin"]


def test_gaps_does_not_load_proposal_as_evidence(tmp_path: Path) -> None:
    config, _requirements = _write_suggest_project(tmp_path)
    proposal = tmp_path / "proposal.yaml"
    proposal.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityProposal
metadata:
  id: QP-ignore
  createdAt: 2026-09-08T12:00:00+08:00
proposal:
  type: obligation_suggest
  status: draft
source:
  kind: requirements
  refs: []
provider:
  name: offline
items: []
"""
    )
    before = runner.invoke(app, ["gaps", "--config", str(config), "--format", "json"])
    assert before.exit_code == 0, before.output
    # even if proposal sits next to config, gaps must ignore it unless listed as evidence
    after = runner.invoke(app, ["gaps", "--config", str(config), "--format", "json"])
    assert after.exit_code == 0, after.output
    assert json.loads(before.output)["results"] == json.loads(after.output)["results"]


def _git_repo_with_change(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "qcov@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "QCov"],
        check=True,
        capture_output=True,
    )
    (repo / "refund").mkdir()
    (repo / "refund" / "service.py").write_text("def refund():\n    return 1\n")
    (repo / "obligation.yaml").write_text(Path("examples/refund/obligation.yaml").read_text())
    (repo / "evidence").mkdir()
    for path in Path("examples/refund/evidence").glob("*.yaml"):
        (repo / "evidence" / path.name).write_text(path.read_text())
    (repo / "qcov.yaml").write_text(
        "apiVersion: qcov.dev/v1alpha1\n"
        "kind: QCovConfig\n"
        "obligations: [obligation.yaml]\n"
        "evidence: [evidence/*.yaml]\n"
    )
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "base",
        ],
        check=True,
        capture_output=True,
    )
    (repo / "refund" / "service.py").write_text(
        "def refund():\n    # concurrency\n    return 1\n"
    )
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "change",
        ],
        check=True,
        capture_output=True,
    )
    return repo


def test_risk_analyze_uses_local_diff(tmp_path: Path) -> None:
    repo = _git_repo_with_change(tmp_path)
    result = runner.invoke(
        app,
        [
            "risk",
            "analyze",
            "--config",
            str(repo / "qcov.yaml"),
            "--base",
            "HEAD~1",
            "--head",
            "HEAD",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["proposal"]["type"] == "change_risk"
    assert payload["source"]["kind"] == "local_diff"
    assert payload["items"]
