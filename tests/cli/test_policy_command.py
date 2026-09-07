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
