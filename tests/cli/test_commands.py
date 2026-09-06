from pathlib import Path

from typer.testing import CliRunner

from qcov.cli.app import app

ROOT = Path(__file__).parents[2]
OBLIGATION = ROOT / "examples/refund/obligation.yaml"
EVIDENCE = ROOT / "examples/refund/evidence"
runner = CliRunner()


def test_gaps_reports_refund_missing_evidence() -> None:
    result = runner.invoke(app, ["gaps", "--obligation", str(OBLIGATION), "--evidence", str(EVIDENCE)])

    assert result.exit_code == 0
    assert "QO-REFUND-001" in result.stdout
    assert "concurrency" in result.stdout


def test_check_fails_for_partial_result() -> None:
    result = runner.invoke(app, ["check", "--obligation", str(OBLIGATION), "--evidence", str(EVIDENCE)])

    assert result.exit_code == 2


def test_inspect_and_report_emit_requested_result(tmp_path: Path) -> None:
    report = tmp_path / "report.json"

    inspect = runner.invoke(
        app,
        ["inspect", "QO-REFUND-001", "--obligation", str(OBLIGATION), "--evidence", str(EVIDENCE)],
    )
    write = runner.invoke(
        app,
        [
            "report",
            "--obligation",
            str(OBLIGATION),
            "--evidence",
            str(EVIDENCE),
            "--output",
            str(report),
            "--format",
            "json",
        ],
    )

    assert inspect.exit_code == 0
    assert write.exit_code == 0
    assert '"obligationId"' in report.read_text()


def test_init_refuses_to_overwrite_configuration(tmp_path: Path) -> None:
    assert runner.invoke(app, ["init", "--path", str(tmp_path)]).exit_code == 0
    assert runner.invoke(app, ["init", "--path", str(tmp_path)]).exit_code == 4


def test_init_creates_a_config_that_scan_can_load(tmp_path: Path) -> None:
    assert runner.invoke(app, ["init", "--path", str(tmp_path)]).exit_code == 0

    result = runner.invoke(app, ["scan", "--config", str(tmp_path / "qcov.yaml")])

    assert result.exit_code == 0


def test_scan_json_lists_junit_file_and_record_count(tmp_path: Path) -> None:
    (tmp_path / "junit.xml").write_text('<testsuite><testcase name="works" /></testsuite>')
    config = tmp_path / "qcov.yaml"
    config.write_text("apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\nscan:\n  junit: [junit.xml]\n")

    result = runner.invoke(app, ["scan", "--config", str(config), "--format", "json"])

    assert result.exit_code == 0
    assert '"adapter": "junit"' in result.stdout
    assert '"recordCount": 1' in result.stdout


def test_gaps_loads_paths_from_config(tmp_path: Path) -> None:
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        f"obligations: [{OBLIGATION}]\n"
        f"evidence: [{EVIDENCE}/*.yaml]\n"
    )

    result = runner.invoke(app, ["gaps", "--config", str(config)])

    assert result.exit_code == 0
    assert "QO-REFUND-001" in result.stdout


def test_config_uses_explicit_obligation_when_only_obligation_is_provided(tmp_path: Path) -> None:
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        "obligations: [missing.yaml]\n"
        f"evidence: [{EVIDENCE}/*.yaml]\n"
    )

    result = runner.invoke(app, ["gaps", "--config", str(config), "--obligation", str(OBLIGATION)])

    assert result.exit_code == 0
    assert "QO-REFUND-001" in result.stdout


def test_config_uses_explicit_evidence_when_only_evidence_is_provided(tmp_path: Path) -> None:
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        f"obligations: [{OBLIGATION}]\n"
        "evidence: [missing/*.yaml]\n"
    )

    result = runner.invoke(app, ["gaps", "--config", str(config), "--evidence", str(EVIDENCE)])

    assert result.exit_code == 0
    assert "QO-REFUND-001" in result.stdout


def test_gaps_accepts_the_documented_plural_obligations_alias() -> None:
    result = runner.invoke(
        app,
        ["gaps", "--obligations", str(OBLIGATION), "--evidence", str(EVIDENCE)],
    )

    assert result.exit_code == 0
