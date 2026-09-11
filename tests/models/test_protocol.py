from __future__ import annotations

import pytest

from qcov.models.protocol import ProductionObservationReport


def test_production_observation_report_rejects_timezone_less_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ProductionObservationReport.model_validate(
            {
                "apiVersion": "qcov.dev/v1alpha1",
                "kind": "ProductionObservationReport",
                "metadata": {"id": "checkout-release"},
                "observations": [
                    {
                        "id": "availability",
                        "category": "runtime",
                        "status": "passed",
                        "timestamp": "2026-09-11T00:00:00",
                    }
                ],
            }
        )
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


VALID_PROPOSAL = {
    "apiVersion": "qcov.dev/v1alpha1",
    "kind": "QualityProposal",
    "metadata": {"id": "QP-20260908-001", "createdAt": "2026-09-08T12:00:00+08:00"},
    "proposal": {"type": "obligation_suggest", "status": "draft"},
    "source": {"kind": "requirements", "refs": ["requirements.md"]},
    "provider": {"name": "offline", "model": None},
    "items": [
        {
            "id": "item-1",
            "kind": "proposed_obligation",
            "obligationRef": "QO-REFUND-003",
            "summary": {
                "en": "Concurrent refund",
                "zh-CN": "并发退款",
            },
            "detail": {"suggestedEvidence": ["concurrency_test"]},
        }
    ],
}


def test_quality_proposal_accepts_draft_obligation_suggest() -> None:
    from qcov.models.protocol import QualityProposal

    proposal = QualityProposal.model_validate(VALID_PROPOSAL)
    assert proposal.proposal.type == "obligation_suggest"
    assert proposal.proposal.status == "draft"
    assert proposal.items[0].obligation_ref == "QO-REFUND-003"


def test_quality_proposal_rejects_non_draft_status() -> None:
    from qcov.models.protocol import QualityProposal

    payload = {
        **VALID_PROPOSAL,
        "proposal": {"type": "obligation_suggest", "status": "approved"},
    }
    with pytest.raises(ValidationError):
        QualityProposal.model_validate(payload)


VALID_QUALITY_PLAN = {
    "apiVersion": "qcov.dev/v1alpha1",
    "kind": "QualityProposal",
    "metadata": {
        "id": "QP-plan-001",
        "createdAt": "2026-09-08T12:00:00+08:00",
    },
    "proposal": {"type": "quality_plan", "status": "draft"},
    "source": {"kind": "evaluation_gaps", "refs": ["qcov.yaml"]},
    "provider": {"name": "offline", "model": None},
    "items": [
        {
            "id": "plan-QO-REFUND-001-behavior",
            "kind": "planned_verification",
            "obligationRef": "QO-REFUND-001",
            "summary": {
                "en": "Prefer api_test for behavior gap",
                "zh-CN": "优先用 api_test 补齐 behavior 缺口",
            },
            "detail": {
                "dimension": "behavior",
                "gapStatus": "MISSING",
                "missingEvidenceTypes": ["api_test"],
                "suggestedEvidenceType": "api_test",
                "benefitScore": 100,
                "costScore": 10,
                "priorityScore": -90,
                "rank": 1,
            },
        }
    ],
}


def test_quality_proposal_accepts_quality_plan() -> None:
    from qcov.models.protocol import QualityProposal

    proposal = QualityProposal.model_validate(VALID_QUALITY_PLAN)
    assert proposal.proposal.type == "quality_plan"
    assert proposal.proposal.status == "draft"
    assert proposal.source.kind == "evaluation_gaps"
    assert proposal.items[0].kind == "planned_verification"


def test_quality_proposal_rejects_invalid_quality_plan_enums() -> None:
    from qcov.models.protocol import QualityProposal

    bad_type = {
        **VALID_QUALITY_PLAN,
        "proposal": {"type": "quality_planner", "status": "draft"},
    }
    with pytest.raises(ValidationError):
        QualityProposal.model_validate(bad_type)

    bad_source = {
        **VALID_QUALITY_PLAN,
        "source": {"kind": "gap_report", "refs": []},
    }
    with pytest.raises(ValidationError):
        QualityProposal.model_validate(bad_source)

    bad_item = {
        **VALID_QUALITY_PLAN,
        "items": [
            {
                **VALID_QUALITY_PLAN["items"][0],
                "kind": "planned_action",
            }
        ],
    }
    with pytest.raises(ValidationError):
        QualityProposal.model_validate(bad_item)
