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


VALID_MAPPING = {
    "apiVersion": "qcov.dev/v1alpha1",
    "kind": "EvidenceMapping",
    "metadata": {"id": "refund-import-mapping"},
    "defaultTimestamp": "2026-09-08T00:00:00+08:00",
    "mappings": [
        {
            "from": {"producer": "junit", "identity": "refund.api::refund_is_accepted"},
            "to": {
                "obligationRef": "QO-REFUND-001",
                "dimension": "behavior",
                "type": "api_test",
            },
        }
    ],
}


def test_evidence_mapping_accepts_junit_and_playwright_producers() -> None:
    from qcov.models.protocol import EvidenceMapping

    mapping = EvidenceMapping.model_validate(VALID_MAPPING)
    assert mapping.metadata.id == "refund-import-mapping"
    assert mapping.mappings[0].from_.producer == "junit"


def test_evidence_mapping_rejects_coverage_producer() -> None:
    from qcov.models.protocol import EvidenceMapping

    payload = {
        **VALID_MAPPING,
        "mappings": [
            {
                "from": {"producer": "coverage.py", "identity": "src/app.py"},
                "to": {
                    "obligationRef": "QO-REFUND-001",
                    "dimension": "behavior",
                    "type": "line_coverage",
                },
            }
        ],
    }
    with pytest.raises(ValidationError):
        EvidenceMapping.model_validate(payload)


def test_evidence_mapping_rejects_naive_default_timestamp() -> None:
    from qcov.models.protocol import EvidenceMapping

    payload = {**VALID_MAPPING, "defaultTimestamp": "2026-09-08T00:00:00"}
    with pytest.raises(ValidationError, match="timezone-aware"):
        EvidenceMapping.model_validate(payload)


def test_evidence_mapping_rejects_duplicate_quintuples() -> None:
    from qcov.models.protocol import EvidenceMapping

    entry = VALID_MAPPING["mappings"][0]
    payload = {**VALID_MAPPING, "mappings": [entry, entry]}
    with pytest.raises(ValidationError, match="duplicate mapping quintuple"):
        EvidenceMapping.model_validate(payload)
