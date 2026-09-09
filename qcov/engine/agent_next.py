"""Select next planned verification actions from a quality_plan proposal."""

from __future__ import annotations

from typing import Literal

from qcov.engine.plan_detail import planned_verification_detail
from qcov.models.agent_contract import NextItem, NextPayload
from qcov.models.errors import AgentInputError
from qcov.models.protocol import QualityProposal


def select_next_actions(
    proposal: QualityProposal,
    *,
    limit: int,
    source: Literal["plan_file", "evaluation"],
) -> NextPayload:
    if proposal.proposal.type != "quality_plan":
        raise AgentInputError(
            AgentInputError.CODE_NOT_QUALITY_PLAN,
            "proposal type must be quality_plan",
        )
    if limit < 1:
        raise AgentInputError(
            AgentInputError.CODE_INVALID_LIMIT,
            "--limit must be >= 1",
        )
    ordered = sorted(
        proposal.items,
        key=lambda item: planned_verification_detail(item).rank,
    )
    items: list[NextItem] = []
    for item in ordered[:limit]:
        detail = planned_verification_detail(item)
        if item.obligation_ref is None:
            raise AgentInputError(
                AgentInputError.CODE_TARGET_NOT_FOUND,
                f"plan item missing obligationRef: {item.id}",
            )
        items.append(
            NextItem.model_validate(
                {
                    "id": item.id,
                    "obligationRef": item.obligation_ref,
                    "dimension": detail.dimension,
                    "suggestedEvidenceType": detail.suggested_evidence_type,
                    "rank": detail.rank,
                    "priorityScore": detail.priority_score,
                }
            )
        )
    return NextPayload.model_validate(
        {
            "source": source,
            "limit": limit,
            "items": [item.model_dump(by_alias=True, mode="json") for item in items],
        }
    )
