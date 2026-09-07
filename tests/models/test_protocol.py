from __future__ import annotations

import pytest
from pydantic import ValidationError

from qcov.models.protocol import QualityEvidence, QualityPolicy, TestingObligation

VALID_EVIDENCE = {
    "apiVersion": "qcov.dev/v1alpha1",
    "kind": "QualityEvidence",
    "metadata": {"id": "QE-001"},
    "obligation": {"ref": "QO-REFUND-001"},
    "evidence": {"dimension": "behavior", "type": "api_test"},
    "producer": {"name": "pytest"},
    "execution": {"status": "passed", "timestamp": "2026-09-02T00:00:00+00:00"},
    "artifact": {"path": "tests/test_refund.py"},
    "confidence": {"deterministic": True, "reproducible": True},
}


def test_obligation_requires_a_localized_title() -> None:
    with pytest.raises(ValidationError):
        TestingObligation.model_validate(
            {"apiVersion": "qcov.dev/v1alpha1", "kind": "TestingObligation"}
        )


def test_evidence_references_an_obligation() -> None:
    evidence = QualityEvidence.model_validate(VALID_EVIDENCE)
    assert evidence.obligation.ref == "QO-REFUND-001"


def test_policy_rejects_empty_allowed_statuses() -> None:
    with pytest.raises(ValidationError) as error:
        QualityPolicy.model_validate(
            {
                "apiVersion": "qcov.dev/v1alpha1",
                "kind": "QualityPolicy",
                "metadata": {"id": "release"},
                "rules": {"default": {"allowedStatuses": []}},
                "waivers": [],
            }
        )
    assert any(item["loc"] == ("rules", "default", "allowedStatuses") for item in error.value.errors())


def test_policy_rejects_duplicate_waiver_obligation_refs() -> None:
    with pytest.raises(ValidationError, match="duplicate waiver obligation reference"):
        QualityPolicy.model_validate(
            {
                "apiVersion": "qcov.dev/v1alpha1",
                "kind": "QualityPolicy",
                "metadata": {"id": "release"},
                "rules": {"default": {"allowedStatuses": ["COVERED"]}},
                "waivers": [
                    {
                        "obligationRef": "QO-001",
                        "reason": "temporary exception",
                        "expiresAt": "2026-10-01T00:00:00+08:00",
                    },
                    {
                        "obligationRef": "QO-001",
                        "reason": "duplicate exception",
                        "expiresAt": "2026-10-01T00:00:00+08:00",
                    },
                ],
            }
        )
