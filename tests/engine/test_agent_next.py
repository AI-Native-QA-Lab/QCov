from __future__ import annotations

import pytest

from qcov.engine.agent_next import select_next_actions
from qcov.engine.gaps import evaluate_obligation
from qcov.engine.planner import build_quality_plan
from qcov.models.errors import AgentInputError
from qcov.models.protocol import QualityProposal, TestingObligation


def _obl() -> TestingObligation:
    return TestingObligation.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "TestingObligation",
            "metadata": {"id": "QO-REFUND-001", "title": {"en": "Refund", "zh-CN": "退款"}},
            "source": {"type": "requirement", "ref": "REFUND-001"},
            "risk": {"domain": "financial", "severity": "critical"},
            "requiredEvidence": {
                "behavior": ["api_test"],
                "boundary": ["property_test"],
            },
        }
    )


def test_select_next_matches_planner_first_item() -> None:
    obl = _obl()
    result = evaluate_obligation(obl, [])
    plan = build_quality_plan([result], [obl], refs=["fixture"])
    payload = select_next_actions(plan, limit=1, source="evaluation")
    assert payload.limit == 1
    assert len(payload.items) == 1
    assert payload.items[0].id == plan.items[0].id
    assert payload.items[0].rank == 1


def test_select_next_empty_plan() -> None:
    plan = QualityProposal.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityProposal",
            "metadata": {"id": "QP-empty", "createdAt": "2026-09-08T00:00:00+00:00"},
            "proposal": {"type": "quality_plan", "status": "draft"},
            "source": {"kind": "evaluation_gaps", "refs": []},
            "provider": {"name": "offline", "model": None},
            "items": [],
        }
    )
    payload = select_next_actions(plan, limit=1, source="plan_file")
    assert payload.items == []


def test_select_next_rejects_non_quality_plan() -> None:
    plan = QualityProposal.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityProposal",
            "metadata": {"id": "QP-x", "createdAt": "2026-09-08T00:00:00+00:00"},
            "proposal": {"type": "obligation_suggest", "status": "draft"},
            "source": {"kind": "requirements", "refs": []},
            "provider": {"name": "offline", "model": None},
            "items": [],
        }
    )
    with pytest.raises(AgentInputError) as exc:
        select_next_actions(plan, limit=1, source="plan_file")
    assert exc.value.code == AgentInputError.CODE_NOT_QUALITY_PLAN
