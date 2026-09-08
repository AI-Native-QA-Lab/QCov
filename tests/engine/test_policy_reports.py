import json
from datetime import datetime

from qcov.engine.policy import PolicyDecision, PolicyReport, PolicyResult, PolicyViolation
from qcov.engine.policy_reports import render_policy_json, render_policy_markdown
from qcov.models.protocol import CoverageStatus


def sample_policy_report() -> PolicyReport:
    return PolicyReport(
        policy_id="release",
        evaluated_at=datetime.fromisoformat("2026-09-07T00:00:00+08:00"),
        results=(
            PolicyResult(
                obligation_id="QO-001",
                coverage_status=CoverageStatus.PARTIAL,
                decision=PolicyDecision.BLOCK,
                violations=(PolicyViolation("QCOV-POLICY-001"),),
                waiver=None,
            ),
        ),
    )


def test_policy_json_uses_stable_machine_keys() -> None:
    payload = json.loads(render_policy_json(sample_policy_report()))

    assert payload["policyId"] == "release"
    assert payload["results"][0]["decision"] == "BLOCK"
    assert "/Users/" not in json.dumps(payload)


def test_policy_markdown_localizes_labels_not_codes() -> None:
    output = render_policy_markdown(sample_policy_report(), locale="zh-CN")

    assert "策略决定" in output
    assert "QCOV-POLICY-001" in output
