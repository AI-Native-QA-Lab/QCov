import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from qcov.cli.app import app

runner = CliRunner()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def _commit(repo: Path) -> str:
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "test")
    return _git(repo, "rev-parse", "HEAD")


def _write_project(tmp_path: Path) -> tuple[Path, Path]:
    obligation = tmp_path / "obligation.yaml"
    obligation.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: TestingObligation
metadata:
  id: QO-REFUND-001
  title: {en: Refund, zh-CN: 退款}
source: {type: README, ref: README.md#refund}
risk: {domain: billing, severity: high}
requiredEvidence:
  behavior: [example]
"""
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\nobligations: [obligation.yaml]\n"
    )
    impact_config = tmp_path / "impact.yaml"
    impact_config.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityImpactConfig
mappings:
  - id: refund
    paths: [src/refund/**]
    obligations: [QO-REFUND-001]
"""
    )
    return config, impact_config


def test_impact_direct_mode_emits_versioned_json(tmp_path: Path) -> None:
    config, impact_config = _write_project(tmp_path)

    result = runner.invoke(
        app,
        [
            "impact",
            "--config",
            str(config),
            "--impact-config",
            str(impact_config),
            "--changed-file",
            "src/refund/service.py",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["contractVersion"] == "qcov.impact/v1"
    assert payload["changedFiles"] == ["src/refund/service.py"]
    assert payload["affectedObligations"] == ["QO-REFUND-001"]
    assert payload["newGaps"] == []
    assert payload["resolvedGaps"] == []
    assert payload["diagnostics"][0]["code"] == "QCOV-IMPACT-004"
    assert "path" not in payload["diagnostics"][0]


def test_impact_and_affected_normalize_unknown_git_refs_to_impact_input_error(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    config, impact_config = _write_project(tmp_path)
    _commit(tmp_path)

    for command in ("impact", "affected"):
        result = runner.invoke(
            app,
            [
                command,
                "--config",
                str(config),
                "--impact-config",
                str(impact_config),
                "--repo",
                str(tmp_path),
                "--base",
                "does-not-exist",
                "--head",
                "HEAD",
            ],
        )

        assert result.exit_code == 4
        assert "QCOV-IMPACT-001" in result.stderr


def test_impact_rejects_mixed_direct_and_snapshot_inputs(tmp_path: Path) -> None:
    config, impact_config = _write_project(tmp_path)

    result = runner.invoke(
        app,
        [
            "impact",
            "--config",
            str(config),
            "--impact-config",
            str(impact_config),
            "--changed-file",
            "src/refund/service.py",
            "--base",
            "HEAD~1",
            "--head",
            "HEAD",
        ],
    )

    assert result.exit_code == 4
    assert "QCOV-IMPACT-001" in result.stderr


def test_impact_rejects_mapping_to_unknown_obligation(tmp_path: Path) -> None:
    config, impact_config = _write_project(tmp_path)
    impact_config.write_text(impact_config.read_text().replace("QO-REFUND-001", "QO-UNKNOWN"))

    result = runner.invoke(
        app,
        [
            "impact",
            "--config",
            str(config),
            "--impact-config",
            str(impact_config),
            "--changed-file",
            "src/refund/service.py",
        ],
    )

    assert result.exit_code == 4
    assert "QCOV-IMPACT-003" in result.stderr


def test_impact_git_mode_reports_new_gap_and_affected_key_gap(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    config, impact_config = _write_project(tmp_path)
    evidence = tmp_path / "evidence.yaml"
    evidence.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityEvidence
metadata: {id: E-1}
obligation: {ref: QO-REFUND-001}
evidence: {dimension: behavior, type: example}
producer: {name: test}
execution: {status: passed, timestamp: 2026-09-11T00:00:00+00:00}
artifact: {path: report.xml}
confidence: {deterministic: true, reproducible: true}
"""
    )
    config.write_text(config.read_text().replace("obligations: [obligation.yaml]", "obligations: [obligation.yaml]\nevidence: [evidence.yaml]"))
    (tmp_path / "src/refund").mkdir(parents=True)
    source = tmp_path / "src/refund/service.py"
    source.write_text("covered = True\n")
    base = _commit(tmp_path)
    evidence.write_text(evidence.read_text().replace("status: passed", "status: unknown"))
    source.write_text("covered = False\n")
    head = _commit(tmp_path)

    result = runner.invoke(
        app,
        ["impact", "--config", str(config), "--impact-config", str(impact_config), "--repo", str(tmp_path), "--base", base, "--head", head, "--format", "json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["changedFiles"] == ["evidence.yaml", "src/refund/service.py"]
    assert payload["newGaps"] == [{"obligationId": "QO-REFUND-001", "status": "UNKNOWN", "missingDimensions": ["behavior"]}]


def test_affected_direct_mode_reports_only_noncovered_affected_key_gaps(tmp_path: Path) -> None:
    config, impact_config = _write_project(tmp_path)
    evidence = tmp_path / "evidence.yaml"
    evidence.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityEvidence
metadata: {id: E-1}
obligation: {ref: QO-REFUND-001}
evidence: {dimension: behavior, type: example}
producer: {name: test}
execution: {status: unknown, timestamp: 2026-09-11T00:00:00+00:00}
artifact: {path: report.xml}
confidence: {deterministic: true, reproducible: true}
"""
    )
    config.write_text(config.read_text() + "evidence: [evidence.yaml]\n")

    result = runner.invoke(
        app,
        [
            "affected",
            "--config",
            str(config),
            "--impact-config",
            str(impact_config),
            "--changed-file",
            "src/refund/service.py",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert set(payload) == {
        "contractVersion",
        "changedFiles",
        "affectedObligations",
        "newGaps",
        "resolvedGaps",
        "diagnostics",
        "keyGaps",
    }
    assert payload["contractVersion"] == "qcov.impact/v1"
    assert payload["changedFiles"] == ["src/refund/service.py"]
    assert payload["affectedObligations"] == ["QO-REFUND-001"]
    assert payload["keyGaps"] == [
        {"obligationId": "QO-REFUND-001", "status": "UNKNOWN", "missingDimensions": ["behavior"]}
    ]


def test_affected_git_mode_evaluates_head_without_delta_fields(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    config, impact_config = _write_project(tmp_path)
    evidence = tmp_path / "evidence.yaml"
    evidence.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityEvidence
metadata: {id: E-1}
obligation: {ref: QO-REFUND-001}
evidence: {dimension: behavior, type: example}
producer: {name: test}
execution: {status: passed, timestamp: 2026-09-11T00:00:00+00:00}
artifact: {path: report.xml}
confidence: {deterministic: true, reproducible: true}
"""
    )
    config.write_text(config.read_text() + "evidence: [evidence.yaml]\n")
    (tmp_path / "src/refund").mkdir(parents=True)
    source = tmp_path / "src/refund/service.py"
    source.write_text("covered = True\n")
    base = _commit(tmp_path)
    evidence.write_text(evidence.read_text().replace("status: passed", "status: unknown"))
    source.write_text("covered = False\n")
    head = _commit(tmp_path)

    result = runner.invoke(
        app,
        ["affected", "--config", str(config), "--impact-config", str(impact_config), "--repo", str(tmp_path), "--base", base, "--head", head, "--format", "json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["changedFiles"] == ["evidence.yaml", "src/refund/service.py"]
    assert payload["keyGaps"] == [
        {"obligationId": "QO-REFUND-001", "status": "UNKNOWN", "missingDimensions": ["behavior"]}
    ]
    assert payload["newGaps"] == []
    assert payload["resolvedGaps"] == []
