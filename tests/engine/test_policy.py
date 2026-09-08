from datetime import datetime

from qcov.engine.gaps import ObligationResult
from qcov.engine.policy import PolicyDecision, PolicyViolation, evaluate_policy
from qcov.models.protocol import CoverageStatus, QualityPolicy

AS_OF = datetime.fromisoformat("2026-09-07T00:00:00+08:00")


def policy(waivers: list[dict[str, str]] | None = None) -> QualityPolicy:
    return QualityPolicy.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityPolicy",
            "metadata": {"id": "release"},
            "rules": {"default": {"allowedStatuses": ["COVERED"]}},
            "waivers": waivers or [],
        }
    )


def result(obligation_id: str, status: CoverageStatus) -> ObligationResult:
    return ObligationResult(obligation_id=obligation_id, status=status, dimensions=())


def test_disallowed_status_blocks_without_waiver() -> None:
    report = evaluate_policy([result("QO-002", CoverageStatus.PARTIAL)], policy(), AS_OF)

    assert report.results[0].decision is PolicyDecision.BLOCK
    assert report.results[0].violations == (PolicyViolation("QCOV-POLICY-001"),)


def test_active_waiver_warns_instead_of_blocking() -> None:
    report = evaluate_policy(
        [result("QO-002", CoverageStatus.PARTIAL)],
        policy(
            [
                {
                    "obligationRef": "QO-002",
                    "reason": "temporary exception",
                    "expiresAt": "2026-10-01T00:00:00+08:00",
                }
            ]
        ),
        AS_OF,
    )

    assert report.results[0].decision is PolicyDecision.WARN


def test_expired_waiver_blocks_disallowed_status_at_expiry_boundary() -> None:
    report = evaluate_policy(
        [result("QO-002", CoverageStatus.PARTIAL)],
        policy(
            [
                {
                    "obligationRef": "QO-002",
                    "reason": "expired exception",
                    "expiresAt": "2026-09-07T00:00:00+08:00",
                }
            ]
        ),
        AS_OF,
    )

    assert report.results[0].violations == (PolicyViolation("QCOV-POLICY-002"),)


def test_policy_results_are_sorted_by_obligation_id() -> None:
    report = evaluate_policy(
        [result("QO-010", CoverageStatus.COVERED), result("QO-002", CoverageStatus.COVERED)],
        policy(),
        AS_OF,
    )

    assert [item.obligation_id for item in report.results] == ["QO-002", "QO-010"]


def test_expired_waiver_on_allowed_status_is_marked_for_cleanup() -> None:
    report = evaluate_policy(
        [result("QO-002", CoverageStatus.COVERED)],
        policy([{"obligationRef": "QO-002", "reason": "expired", "expiresAt": "2026-09-07T00:00:00+08:00"}]),
        AS_OF,
    )

    assert report.results[0].decision is PolicyDecision.WARN
    assert report.results[0].waiver_expired is True
