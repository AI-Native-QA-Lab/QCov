from __future__ import annotations

import pytest

from qcov.ai import (
    ChangeRiskContext,
    ObligationSuggestContext,
    OfflineProvider,
    analyze_change,
    propose_obligations,
    resolve_provider,
)
from qcov.models.errors import ProposalInputError
from qcov.models.protocol import TestingObligation


def _obligation() -> TestingObligation:
    return TestingObligation.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "TestingObligation",
            "metadata": {
                "id": "QO-REFUND-001",
                "title": {"en": "Refund", "zh-CN": "退款"},
            },
            "source": {"type": "requirement", "ref": "REFUND-001"},
            "risk": {"domain": "financial", "severity": "critical"},
            "requiredEvidence": {"behavior": ["api_test"]},
        }
    )


def test_offline_propose_obligations_returns_draft_with_mentioned_id() -> None:
    context = ObligationSuggestContext(
        requirements_text="Please cover QO-REFUND-001 concurrency gaps.",
        requirements_refs=["requirements.md"],
        obligations=(_obligation(),),
    )
    proposal = propose_obligations(context, OfflineProvider())
    assert proposal.kind == "QualityProposal"
    assert proposal.proposal.type == "obligation_suggest"
    assert proposal.proposal.status == "draft"
    assert proposal.provider.name == "offline"
    assert any(item.obligation_ref == "QO-REFUND-001" for item in proposal.items)


def test_propose_obligations_requires_requirements_text() -> None:
    context = ObligationSuggestContext(
        requirements_text="   ",
        requirements_refs=[],
        obligations=(_obligation(),),
    )
    with pytest.raises(ProposalInputError, match="QCOV-PROPOSAL-002"):
        propose_obligations(context, OfflineProvider())


def test_analyze_change_returns_change_risk_draft() -> None:
    context = ChangeRiskContext(
        diff_text="diff --git a/refund/service.py b/refund/service.py\n+concurrency",
        base_ref="HEAD~1",
        head_ref="HEAD",
        obligations=(_obligation(),),
    )
    proposal = analyze_change(context, OfflineProvider())
    assert proposal.proposal.type == "change_risk"
    assert proposal.source.kind == "local_diff"
    assert proposal.items


def test_offline_propose_is_deterministic() -> None:
    context = ObligationSuggestContext(
        requirements_text="Please cover QO-REFUND-001 concurrency gaps.",
        requirements_refs=["requirements.md"],
        obligations=(_obligation(),),
    )
    first = propose_obligations(context, OfflineProvider())
    second = propose_obligations(context, OfflineProvider())
    assert first.metadata.id == second.metadata.id
    assert first.metadata.created_at == second.metadata.created_at
    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_analyze_change_does_not_match_on_concurrency_alone() -> None:
    other = TestingObligation.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "TestingObligation",
            "metadata": {
                "id": "QO-OTHER-001",
                "title": {"en": "Other", "zh-CN": "其他"},
            },
            "source": {"type": "requirement", "ref": "OTHER-001"},
            "risk": {"domain": "financial", "severity": "critical"},
            "requiredEvidence": {"behavior": ["api_test"]},
        }
    )
    context = ChangeRiskContext(
        diff_text="diff --git a/foo.py b/foo.py\n+concurrency helper",
        base_ref="HEAD~1",
        head_ref="HEAD",
        obligations=(_obligation(), other),
    )
    proposal = analyze_change(context, OfflineProvider())
    # No id/ref hit → single fallback to first obligation only
    assert [item.obligation_ref for item in proposal.items] == ["QO-REFUND-001"]


def test_provider_exception_maps_to_ai_002() -> None:
    class Boom:
        name = "boom"

        def propose_obligations(self, context: ObligationSuggestContext) -> object:
            raise RuntimeError("network down")

        def analyze_change(self, context: ChangeRiskContext) -> object:
            raise RuntimeError("network down")

    context = ObligationSuggestContext(
        requirements_text="anything",
        requirements_refs=[],
        obligations=(_obligation(),),
    )
    with pytest.raises(ProposalInputError, match="QCOV-AI-002"):
        propose_obligations(context, Boom())  # type: ignore[arg-type]


def test_resolve_provider_unknown_raises_ai_001() -> None:
    with pytest.raises(ProposalInputError, match="QCOV-AI-001"):
        resolve_provider("missing-provider")
