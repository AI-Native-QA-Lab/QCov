"""Deterministic quality plan builder from evaluation gaps."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

from qcov.engine.gaps import ObligationResult
from qcov.models.protocol import (
    CoverageStatus,
    ProposalItem,
    QualityDimension,
    QualityProposal,
    TestingObligation,
)

_OFFLINE_CREATED_AT = "1970-01-01T00:00:00+00:00"

_STATUS_BENEFIT: dict[CoverageStatus, int] = {
    CoverageStatus.MISSING: 50,
    CoverageStatus.UNKNOWN: 20,
}

_SEVERITY_BENEFIT: dict[str, int] = {
    "critical": 40,
    "high": 30,
    "medium": 20,
    "low": 10,
}
_DEFAULT_SEVERITY_BENEFIT = 15

_DIMENSION_BENEFIT: dict[QualityDimension, int] = {
    QualityDimension.SECURITY: 25,
    QualityDimension.FAULT: 25,
    QualityDimension.PRODUCTION: 25,
    QualityDimension.CONCURRENCY: 20,
    QualityDimension.IDEMPOTENCY: 20,
    QualityDimension.DATA: 20,
    QualityDimension.BOUNDARY: 15,
    QualityDimension.INTEGRATION: 15,
    QualityDimension.BEHAVIOR: 10,
}

_COST_BY_TYPE: dict[str, int] = {
    "api_test": 10,
    "junit_test": 10,
    "pytest_marker": 10,
    "property_test": 20,
    "database_invariant": 20,
    "e2e_test": 35,
    "playwright_test": 35,
    "production_signal": 50,
    "manual_review": 50,
}
_DEFAULT_COST = 40
_EMPTY_REQUIRED_TYPES_COST = 40


def _stable_proposal_id(proposal_type: str, refs: list[str], item_ids: list[str]) -> str:
    digest = hashlib.sha256(
        "\0".join([proposal_type, *refs, *item_ids]).encode("utf-8")
    ).hexdigest()[:12]
    return f"QP-{digest}"


def _severity_benefit(severity: str) -> int:
    return _SEVERITY_BENEFIT.get(severity.lower(), _DEFAULT_SEVERITY_BENEFIT)


def _dimension_benefit(dimension: QualityDimension) -> int:
    return _DIMENSION_BENEFIT[dimension]


def _type_cost(evidence_type: str) -> int:
    return _COST_BY_TYPE.get(evidence_type, _DEFAULT_COST)


def _pick_suggested_type(required_types: tuple[str, ...]) -> tuple[str | None, int]:
    if not required_types:
        return None, _EMPTY_REQUIRED_TYPES_COST
    best_cost = min(_type_cost(item) for item in required_types)
    candidates = sorted(item for item in required_types if _type_cost(item) == best_cost)
    return candidates[0], best_cost


@dataclass(frozen=True)
class PlanRow:
    obligation_id: str
    dimension: QualityDimension
    gap_status: CoverageStatus
    missing_evidence_types: tuple[str, ...]
    suggested_evidence_type: str | None
    benefit_score: int
    cost_score: int
    priority_score: int


def _benefit_score(
    status: CoverageStatus,
    severity: str,
    dimension: QualityDimension,
) -> int:
    return (
        _STATUS_BENEFIT[status]
        + _severity_benefit(severity)
        + _dimension_benefit(dimension)
    )


def _collect_rows(
    results: Sequence[ObligationResult],
    obligations_by_id: dict[str, TestingObligation],
) -> list[PlanRow]:
    rows: list[PlanRow] = []
    for result in results:
        obligation = obligations_by_id[result.obligation_id]
        severity = obligation.risk.severity
        for dim_result in result.unproven_dimensions:
            missing_types = tuple(sorted(dim_result.required_types))
            suggested, cost = _pick_suggested_type(dim_result.required_types)
            benefit = _benefit_score(dim_result.status, severity, dim_result.dimension)
            rows.append(
                PlanRow(
                    obligation_id=result.obligation_id,
                    dimension=dim_result.dimension,
                    gap_status=dim_result.status,
                    missing_evidence_types=missing_types,
                    suggested_evidence_type=suggested,
                    benefit_score=benefit,
                    cost_score=cost,
                    priority_score=cost - benefit,
                )
            )
    return rows


def _sort_rows(rows: list[PlanRow]) -> list[PlanRow]:
    def sort_key(row: PlanRow) -> tuple[int, str, str, str]:
        first_missing = row.missing_evidence_types[0] if row.missing_evidence_types else ""
        return (
            row.priority_score,
            row.obligation_id,
            row.dimension.value,
            first_missing,
        )

    return sorted(rows, key=sort_key)


def _summary_en(
    rank: int,
    dimension: QualityDimension,
    obligation_id: str,
    suggested: str | None,
) -> str:
    via = suggested if suggested is not None else "unspecified evidence"
    return f"Rank {rank}: verify {dimension.value} for {obligation_id} via {via}"


def _summary_zh(
    rank: int,
    dimension: QualityDimension,
    obligation_id: str,
    suggested: str | None,
) -> str:
    suggested_text = suggested if suggested is not None else "未指定证据"
    return f"第 {rank} 步：为 {obligation_id} 的 {dimension.value} 优先补齐 {suggested_text}"


def build_quality_plan(
    results: Sequence[ObligationResult],
    obligations: Sequence[TestingObligation],
    *,
    refs: Sequence[str],
) -> QualityProposal:
    obligations_by_id = {obligation.metadata.id: obligation for obligation in obligations}
    rows = _sort_rows(_collect_rows(results, obligations_by_id))

    items: list[ProposalItem] = []
    for rank, row in enumerate(rows, start=1):
        items.append(
            ProposalItem.model_validate(
                {
                    "id": f"plan-{row.obligation_id}-{row.dimension.value}",
                    "kind": "planned_verification",
                    "obligationRef": row.obligation_id,
                    "summary": {
                        "en": _summary_en(
                            rank,
                            row.dimension,
                            row.obligation_id,
                            row.suggested_evidence_type,
                        ),
                        "zh-CN": _summary_zh(
                            rank,
                            row.dimension,
                            row.obligation_id,
                            row.suggested_evidence_type,
                        ),
                    },
                    "detail": {
                        "dimension": row.dimension.value,
                        "gapStatus": row.gap_status.value,
                        "missingEvidenceTypes": list(row.missing_evidence_types),
                        "suggestedEvidenceType": row.suggested_evidence_type,
                        "benefitScore": row.benefit_score,
                        "costScore": row.cost_score,
                        "priorityScore": row.priority_score,
                        "rank": rank,
                    },
                }
            )
        )

    ref_list = list(refs)
    item_ids = [item.id for item in items]
    return QualityProposal.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityProposal",
            "metadata": {
                "id": _stable_proposal_id("quality_plan", ref_list, item_ids),
                "createdAt": _OFFLINE_CREATED_AT,
            },
            "proposal": {"type": "quality_plan", "status": "draft"},
            "source": {"kind": "evaluation_gaps", "refs": ref_list},
            "provider": {"name": "offline", "model": None},
            "items": [item.model_dump(by_alias=True, mode="json") for item in items],
        }
    )
