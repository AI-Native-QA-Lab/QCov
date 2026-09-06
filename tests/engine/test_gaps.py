from __future__ import annotations

import pytest

from qcov.engine.gaps import evaluate_obligation
from qcov.models.protocol import CoverageStatus, QualityEvidence, TestingObligation


def obligation() -> TestingObligation:
    return TestingObligation.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "TestingObligation",
            "metadata": {"id": "QO-REFUND-001", "title": {"en": "Refund", "zh-CN": "退款"}},
            "source": {"type": "requirement", "ref": "REFUND-001"},
            "risk": {"domain": "financial", "severity": "critical"},
            "requiredEvidence": {"behavior": ["api_test"], "boundary": ["property_test"]},
        }
    )


def passing(dimension: str) -> QualityEvidence:
    evidence_type = "api_test" if dimension == "behavior" else "property_test"
    return QualityEvidence.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityEvidence",
            "metadata": {"id": f"QE-{dimension}"},
            "obligation": {"ref": "QO-REFUND-001"},
            "evidence": {"dimension": dimension, "type": evidence_type},
            "producer": {"name": "pytest"},
            "execution": {"status": "passed", "timestamp": "2026-09-02T00:00:00+00:00"},
            "artifact": {"path": "tests/test_refund.py"},
            "confidence": {"deterministic": True, "reproducible": True},
        }
    )


@pytest.mark.parametrize(
    ("evidence", "expected"),
    [
        ([passing("behavior"), passing("boundary")], CoverageStatus.COVERED),
        ([passing("behavior")], CoverageStatus.PARTIAL),
        ([], CoverageStatus.UNKNOWN),
    ],
)
def test_gap_status_is_deterministic(
    evidence: list[QualityEvidence], expected: CoverageStatus
) -> None:
    assert evaluate_obligation(obligation(), evidence).status is expected


def test_unknown_observation_produces_unknown_status() -> None:
    raw = passing("behavior").model_dump(by_alias=True, mode="json")
    raw["execution"]["status"] = "unknown"
    unknown = QualityEvidence.model_validate(raw)
    assert evaluate_obligation(obligation(), [unknown]).status is CoverageStatus.PARTIAL


def test_unrelated_evidence_does_not_turn_an_absent_obligation_inventory_into_missing() -> None:
    raw = passing("behavior").model_dump(by_alias=True, mode="json")
    raw["obligation"]["ref"] = "QO-OTHER-001"
    unrelated = QualityEvidence.model_validate(raw)

    assert evaluate_obligation(obligation(), [unrelated]).status is CoverageStatus.UNKNOWN
