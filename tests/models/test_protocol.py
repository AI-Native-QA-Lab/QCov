from __future__ import annotations

import pytest
from pydantic import ValidationError

from qcov.models.protocol import QualityEvidence, TestingObligation

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
