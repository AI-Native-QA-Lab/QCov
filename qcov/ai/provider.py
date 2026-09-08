"""AI provider abstractions for proposal-only surfaces."""

from __future__ import annotations

import hashlib
from typing import Literal, Protocol

from qcov.ai.context import (
    ChangeRiskContext,
    ObligationSuggestContext,
)
from qcov.models.errors import ProposalInputError
from qcov.models.protocol import ProposalItem, QualityProposal, TestingObligation

_OFFLINE_CREATED_AT = "1970-01-01T00:00:00+00:00"


class AIProvider(Protocol):
    name: str

    def propose_obligations(self, context: ObligationSuggestContext) -> QualityProposal: ...

    def analyze_change(self, context: ChangeRiskContext) -> QualityProposal: ...


def resolve_provider(name: str) -> AIProvider:
    if name == "offline":
        return OfflineProvider()
    raise ProposalInputError(f"QCOV-AI-001: unknown AI provider: {name}")


def _stable_proposal_id(proposal_type: str, refs: list[str], item_ids: list[str]) -> str:
    digest = hashlib.sha256(
        "\0".join([proposal_type, *refs, *item_ids]).encode("utf-8")
    ).hexdigest()[:12]
    return f"QP-{digest}"


def _draft_proposal(
    *,
    proposal_type: Literal["obligation_suggest", "change_risk"],
    source_kind: Literal["requirements", "local_diff"],
    refs: list[str],
    provider_name: str,
    items: list[ProposalItem],
) -> QualityProposal:
    item_ids = [item.id for item in items]
    return QualityProposal.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityProposal",
            "metadata": {
                "id": _stable_proposal_id(proposal_type, refs, item_ids),
                "createdAt": _OFFLINE_CREATED_AT,
            },
            "proposal": {"type": proposal_type, "status": "draft"},
            "source": {"kind": source_kind, "refs": refs},
            "provider": {"name": provider_name, "model": None},
            "items": [
                item.model_dump(by_alias=True, mode="json") for item in items
            ],
        }
    )


def _item(
    *,
    item_id: str,
    kind: Literal["proposed_obligation", "affected_obligation", "suggested_evidence"],
    obligation_ref: str | None,
    summary_en: str,
    summary_zh: str,
    detail: dict[str, object],
) -> ProposalItem:
    return ProposalItem.model_validate(
        {
            "id": item_id,
            "kind": kind,
            "obligationRef": obligation_ref,
            "summary": {"en": summary_en, "zh-CN": summary_zh},
            "detail": detail,
        }
    )


class OfflineProvider:
    """Deterministic, network-free proposal provider for tests and local use."""

    name = "offline"

    def propose_obligations(self, context: ObligationSuggestContext) -> QualityProposal:
        text = context.requirements_text
        items: list[ProposalItem] = []
        for obligation in context.obligations:
            if obligation.metadata.id in text:
                items.append(
                    _item(
                        item_id=f"item-{obligation.metadata.id}",
                        kind="suggested_evidence",
                        obligation_ref=obligation.metadata.id,
                        summary_en=f"Review evidence gaps for {obligation.metadata.id}",
                        summary_zh=f"复核 {obligation.metadata.id} 的证据缺口",
                        detail={"hint": "offline heuristic mention"},
                    )
                )
        if not items:
            items.append(
                _item(
                    item_id="item-default",
                    kind="proposed_obligation",
                    obligation_ref="QO-PROPOSED-001",
                    summary_en="Proposed obligation from requirements",
                    summary_zh="基于需求的建议义务",
                    detail={"excerpt": text[:200]},
                )
            )
        return _draft_proposal(
            proposal_type="obligation_suggest",
            source_kind="requirements",
            refs=list(context.requirements_refs),
            provider_name=self.name,
            items=items,
        )

    def analyze_change(self, context: ChangeRiskContext) -> QualityProposal:
        items: list[ProposalItem] = []
        lowered = context.diff_text.lower()
        for obligation in context.obligations:
            if _obligation_mentioned_in_diff(obligation, lowered):
                items.append(
                    _item(
                        item_id=f"item-{obligation.metadata.id}",
                        kind="affected_obligation",
                        obligation_ref=obligation.metadata.id,
                        summary_en=f"Change may affect {obligation.metadata.id}",
                        summary_zh=f"变更可能影响 {obligation.metadata.id}",
                        detail={"base": context.base_ref, "head": context.head_ref},
                    )
                )
        if not items and context.obligations:
            obligation = context.obligations[0]
            items.append(
                _item(
                    item_id=f"item-{obligation.metadata.id}",
                    kind="affected_obligation",
                    obligation_ref=obligation.metadata.id,
                    summary_en=f"Review {obligation.metadata.id} against local diff",
                    summary_zh=f"对照本地 diff 复核 {obligation.metadata.id}",
                    detail={"base": context.base_ref, "head": context.head_ref},
                )
            )
        return _draft_proposal(
            proposal_type="change_risk",
            source_kind="local_diff",
            refs=[context.base_ref, context.head_ref],
            provider_name=self.name,
            items=items,
        )


def _obligation_mentioned_in_diff(obligation: TestingObligation, lowered_diff: str) -> bool:
    """Match only explicit obligation id or source.ref tokens in the diff text."""
    return (
        obligation.metadata.id.lower() in lowered_diff
        or obligation.source.ref.lower() in lowered_diff
    )
