from pathlib import Path

from typer.testing import CliRunner

from qcov.cli.app import app

ROOT = Path(__file__).parents[2]
OBLIGATION = ROOT / "examples/refund/obligation.yaml"
EVIDENCE = ROOT / "examples/refund/evidence"
runner = CliRunner()


def test_policy_check_single_obligation_renders_chinese_warning(tmp_path: Path) -> None:
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityPolicy
metadata:
  id: release
rules:
  default:
    allowedStatuses: [COVERED]
waivers:
  - obligationRef: QO-REFUND-001
    reason: local fixture lacks production evidence
    expiresAt: 2026-10-01T00:00:00+08:00
"""
    )
    result = runner.invoke(
        app,
        ["policy", "check", "--obligation", str(OBLIGATION), "--evidence", str(EVIDENCE),
         "--policy", str(policy), "--as-of", "2026-09-07T00:00:00+08:00", "--locale", "zh-CN"],
    )
    assert result.exit_code == 0
    assert "策略决定" in result.stdout


def test_policy_check_rejects_invalid_format_and_locale(tmp_path: Path) -> None:
    policy = tmp_path / "policy.yaml"
    policy.write_text("""apiVersion: qcov.dev/v1alpha1
kind: QualityPolicy
metadata: {id: release}
rules: {default: {allowedStatuses: [COVERED]}}
waivers: []
""")
    base = ["policy", "check", "--obligation", str(OBLIGATION), "--evidence", str(EVIDENCE),
            "--policy", str(policy), "--as-of", "2026-09-07T00:00:00+08:00"]

    assert runner.invoke(app, [*base, "--format", "nope"]).exit_code == 4
    assert runner.invoke(app, [*base, "--locale", "fr"]).exit_code == 4


def test_policy_check_config_renders_json_and_rejects_mixed_inputs(tmp_path: Path) -> None:
    policy = tmp_path / "policy.yaml"
    config = tmp_path / "qcov.yaml"
    policy.write_text("""apiVersion: qcov.dev/v1alpha1
kind: QualityPolicy
metadata: {id: release}
rules: {default: {allowedStatuses: [COVERED]}}
waivers: []
""")
    config.write_text(f"""apiVersion: qcov.dev/v1alpha1
kind: QCovConfig
obligations: [{OBLIGATION}]
evidence: [{EVIDENCE}/*.yaml]
""")
    base = ["policy", "check", "--config", str(config), "--policy", str(policy),
            "--as-of", "2026-09-07T00:00:00+08:00"]

    blocked = runner.invoke(app, [*base, "--format", "json"])
    mixed = runner.invoke(app, [*base, "--obligation", str(OBLIGATION)])

    assert blocked.exit_code == 2
    assert '"coverageStatus": "PARTIAL"' in blocked.stdout
    assert mixed.exit_code == 4
