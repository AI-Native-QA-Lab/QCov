"""Helpers for reading planned_verification proposal item detail."""

from __future__ import annotations

from dataclasses import dataclass

from qcov.models.errors import AgentInputError
from qcov.models.protocol import ProposalItem


@dataclass(frozen=True)
class PlannedVerificationDetail:
    dimension: str
    rank: int
    priority_score: int
    suggested_evidence_type: str | None
    gap_status: str | None
    missing_evidence_types: list[str]


def planned_verification_detail(item: ProposalItem) -> PlannedVerificationDetail:
    if item.kind != "planned_verification":
        raise AgentInputError(
            AgentInputError.CODE_TARGET_NOT_FOUND,
            f"item kind must be planned_verification, got {item.kind}",
        )
    detail = item.detail
    dimension = detail.get("dimension")
    rank = detail.get("rank")
    priority = detail.get("priorityScore")
    if not isinstance(dimension, str):
        raise AgentInputError(
            AgentInputError.CODE_TARGET_NOT_FOUND,
            f"plan item missing dimension: {item.id}",
        )
    if not isinstance(rank, int) or not isinstance(priority, int):
        raise AgentInputError(
            AgentInputError.CODE_TARGET_NOT_FOUND,
            f"plan item missing rank or priorityScore: {item.id}",
        )
    suggested = detail.get("suggestedEvidenceType")
    gap_status = detail.get("gapStatus")
    missing = detail.get("missingEvidenceTypes")
    return PlannedVerificationDetail(
        dimension=dimension,
        rank=rank,
        priority_score=priority,
        suggested_evidence_type=suggested if isinstance(suggested, str) else None,
        gap_status=gap_status if isinstance(gap_status, str) else None,
        missing_evidence_types=list(missing) if isinstance(missing, list) else [],
    )
