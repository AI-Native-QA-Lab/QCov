"""Select next planned verification actions from a quality_plan proposal."""

from __future__ import annotations

from typing import Literal

from qcov.models.agent_contract import NextItem, NextPayload
from qcov.models.errors import AgentInputError
from qcov.models.io import ConfigLoadError
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
        raise ConfigLoadError("QCOV-CLI-007: --limit must be >= 1")
    items: list[NextItem] = []
    for item in proposal.items[:limit]:
        detail = item.detail
        dimension = detail.get("dimension")
        rank = detail.get("rank")
        priority = detail.get("priorityScore")
        if item.obligation_ref is None or not isinstance(dimension, str):
            raise AgentInputError(
                AgentInputError.CODE_TARGET_NOT_FOUND,
                f"plan item missing obligationRef or dimension: {item.id}",
            )
        if not isinstance(rank, int) or not isinstance(priority, int):
            raise AgentInputError(
                AgentInputError.CODE_TARGET_NOT_FOUND,
                f"plan item missing rank or priorityScore: {item.id}",
            )
        suggested = detail.get("suggestedEvidenceType")
        items.append(
            NextItem.model_validate(
                {
                    "id": item.id,
                    "obligationRef": item.obligation_ref,
                    "dimension": dimension,
                    "suggestedEvidenceType": suggested if isinstance(suggested, str) else None,
                    "rank": rank,
                    "priorityScore": priority,
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
