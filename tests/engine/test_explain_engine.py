from __future__ import annotations

import pytest

from qcov.engine.explain import explain_evidence, explain_gap, explain_plan_item
from qcov.engine.gaps import evaluate_obligation
from qcov.models.errors import AgentInputError
from qcov.models.protocol import CoverageStatus, ProposalItem, QualityEvidence, TestingObligation


def _obl() -> TestingObligation:
    return TestingObligation.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "TestingObligation",
            "metadata": {"id": "QO-REFUND-001", "title": {"en": "Refund", "zh-CN": "退款"}},
            "source": {"type": "requirement", "ref": "REFUND-001"},
            "risk": {"domain": "financial", "severity": "critical"},
            "requiredEvidence": {"behavior": ["api_test"]},
        }
    )


def _ev(**overrides: object) -> QualityEvidence:
    raw: dict = {
        "apiVersion": "qcov.dev/v1alpha1",
        "kind": "QualityEvidence",
        "metadata": {"id": "QE-1"},
        "obligation": {"ref": "QO-REFUND-001"},
        "evidence": {"dimension": "behavior", "type": "api_test"},
        "producer": {"name": "pytest"},
        "execution": {"status": "failed", "timestamp": "2026-09-02T00:00:00+00:00"},
        "artifact": {"path": "t.py"},
        "confidence": {"deterministic": True, "reproducible": True},
    }
    for key, value in overrides.items():
        if key == "ref":
            raw["obligation"]["ref"] = value
        elif key == "dimension":
            raw["evidence"]["dimension"] = value
        elif key == "type":
            raw["evidence"]["type"] = value
        elif key == "status":
            raw["execution"]["status"] = value
        elif key == "id":
            raw["metadata"]["id"] = value
    return QualityEvidence.model_validate(raw)


def test_explain_gap_no_evidence_stable_reason_order() -> None:
    obl = _obl()
    result = evaluate_obligation(obl, [])
    payload = explain_gap(obl, result, "behavior")
    codes = [item.code for item in payload.reasons]
    assert codes == sorted(codes)
    assert "NO_EVIDENCE_FOR_OBLIGATION" in codes
    assert payload.status == CoverageStatus.UNKNOWN.value


def test_explain_evidence_emits_mismatch_codes() -> None:
    obl = _obl()
    payload = explain_evidence(
        obl,
        [_ev(ref="QO-OTHER", dimension="boundary", type="e2e_test", status="failed")],
        "behavior",
    )
    codes = {item.code for item in payload.reasons}
    assert "OBLIGATION_REF_MISMATCH" in codes
    assert "DIMENSION_MISMATCH" in codes
    assert "TYPE_NOT_REQUIRED" in codes


def test_explain_gap_already_covered() -> None:
    obl = _obl()
    result = evaluate_obligation(obl, [_ev(status="passed")])
    payload = explain_gap(obl, result, "behavior")
    assert [item.code for item in payload.reasons] == ["ALREADY_COVERED"]


def test_explain_plan_item_reads_detail() -> None:
    item = ProposalItem.model_validate(
        {
            "id": "plan-QO-REFUND-001-behavior",
            "kind": "planned_verification",
            "obligationRef": "QO-REFUND-001",
            "summary": {"en": "step", "zh-CN": "步骤"},
            "detail": {
                "dimension": "behavior",
                "gapStatus": "MISSING",
                "suggestedEvidenceType": "api_test",
                "priorityScore": -90,
                "rank": 1,
            },
        }
    )
    payload = explain_plan_item(item)
    assert payload.mode == "plan_item"
    assert payload.item_id == item.id
    assert payload.rank == 1
    assert payload.priority_score == -90


def test_explain_gap_unknown_dimension_raises() -> None:
    obl = _obl()
    result = evaluate_obligation(obl, [])
    with pytest.raises(AgentInputError) as exc:
        explain_gap(obl, result, "security")
    assert exc.value.code == AgentInputError.CODE_TARGET_NOT_FOUND
