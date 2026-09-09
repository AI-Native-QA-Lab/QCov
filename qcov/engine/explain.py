"""Deterministic explanation of gaps, plan items, and evidence mismatches."""

from __future__ import annotations

from collections.abc import Sequence

from qcov.engine.gaps import DimensionResult, ObligationResult, evaluate_obligation
from qcov.engine.plan_detail import planned_verification_detail
from qcov.models.agent_contract import ExplainPayload, ReasonCode, ReasonItem
from qcov.models.errors import AgentInputError
from qcov.models.protocol import (
    CoverageStatus,
    ProposalItem,
    QualityDimension,
    QualityEvidence,
    TestingObligation,
)

_REASON_SUMMARIES: dict[ReasonCode, dict[str, str]] = {
    "ALREADY_COVERED": {
        "en": "This dimension is already COVERED by passed evidence.",
        "zh-CN": "该维度已被 passed 证据覆盖为 COVERED。",
    },
    "DIMENSION_MISMATCH": {
        "en": "Evidence dimension does not match the target dimension.",
        "zh-CN": "证据维度与目标维度不一致。",
    },
    "NO_EVIDENCE_FOR_OBLIGATION": {
        "en": "No evidence references this obligation.",
        "zh-CN": "没有指向该义务的证据。",
    },
    "OBLIGATION_REF_MISMATCH": {
        "en": "Evidence obligation.ref does not match the target obligation.",
        "zh-CN": "证据的 obligation.ref 与目标义务不匹配。",
    },
    "STATUS_NOT_PASSED": {
        "en": "Matching evidence exists but none has execution.status passed.",
        "zh-CN": "存在匹配证据但无一为 passed。",
    },
    "STATUS_UNKNOWN": {
        "en": "Matching evidence includes unknown status; dimension is UNKNOWN.",
        "zh-CN": "匹配证据含 unknown 状态，维度为 UNKNOWN。",
    },
    "TYPE_NOT_REQUIRED": {
        "en": "Evidence type is not in the dimension requiredTypes.",
        "zh-CN": "证据类型不在该维度 requiredTypes 中。",
    },
}


def _reason(code: ReasonCode) -> ReasonItem:
    summary = _REASON_SUMMARIES[code]
    return ReasonItem.model_validate({"code": code, "summary": summary})


def _sorted_reasons(codes: set[ReasonCode]) -> list[ReasonItem]:
    return [_reason(code) for code in sorted(codes)]


def _parse_dimension(dimension: str) -> QualityDimension:
    try:
        return QualityDimension(dimension)
    except ValueError as error:
        raise AgentInputError(
            AgentInputError.CODE_TARGET_NOT_FOUND,
            f"unknown dimension: {dimension}",
        ) from error


def _dimension_result(
    result: ObligationResult, dimension: QualityDimension
) -> DimensionResult:
    for item in result.dimensions:
        if item.dimension is dimension:
            return item
    raise AgentInputError(
        AgentInputError.CODE_TARGET_NOT_FOUND,
        f"dimension not required by obligation: {dimension.value}",
    )


def explain_gap(
    obligation: TestingObligation,
    result: ObligationResult,
    dimension: str,
) -> ExplainPayload:
    dim = _parse_dimension(dimension)
    if obligation.metadata.id != result.obligation_id:
        raise AgentInputError(
            AgentInputError.CODE_TARGET_NOT_FOUND,
            "obligation id does not match evaluation result",
        )
    dim_result = _dimension_result(result, dim)
    codes: set[ReasonCode] = set()
    if dim_result.status is CoverageStatus.COVERED:
        codes.add("ALREADY_COVERED")
    elif not dim_result.observed_evidence_ids and dim_result.status is CoverageStatus.UNKNOWN:
        # No obligation-scoped evidence → Gap Engine reports UNKNOWN.
        codes.add("NO_EVIDENCE_FOR_OBLIGATION")
    elif dim_result.status is CoverageStatus.UNKNOWN:
        codes.add("STATUS_UNKNOWN")
    elif dim_result.status is CoverageStatus.MISSING:
        if not dim_result.observed_evidence_ids:
            codes.add("NO_EVIDENCE_FOR_OBLIGATION")
        else:
            codes.add("STATUS_NOT_PASSED")
    return ExplainPayload.model_validate(
        {
            "mode": "gap",
            "obligationId": obligation.metadata.id,
            "dimension": dim.value,
            "status": dim_result.status.value,
            "requiredTypes": list(dim_result.required_types),
            "observedEvidenceIds": list(dim_result.observed_evidence_ids),
            "reasons": [item.model_dump(by_alias=True, mode="json") for item in _sorted_reasons(codes)],
        }
    )


def explain_evidence(
    obligation: TestingObligation,
    evidence: Sequence[QualityEvidence],
    dimension: str,
) -> ExplainPayload:
    dim = _parse_dimension(dimension)
    required = tuple(obligation.required_evidence.get(dim, []))
    codes: set[ReasonCode] = set()
    related = [item for item in evidence if item.obligation.ref == obligation.metadata.id]
    if not related:
        codes.add("NO_EVIDENCE_FOR_OBLIGATION")
    for item in evidence:
        if item.obligation.ref != obligation.metadata.id:
            codes.add("OBLIGATION_REF_MISMATCH")
            continue
        if item.evidence.dimension is not dim:
            codes.add("DIMENSION_MISMATCH")
            continue
        if item.evidence.type not in required:
            codes.add("TYPE_NOT_REQUIRED")
            continue
        if item.execution.status == "unknown":
            codes.add("STATUS_UNKNOWN")
        elif item.execution.status != "passed":
            codes.add("STATUS_NOT_PASSED")

    result = evaluate_obligation(obligation, evidence)
    dim_result = _dimension_result(result, dim)
    if dim_result.status is CoverageStatus.COVERED:
        codes = {"ALREADY_COVERED"}

    return ExplainPayload.model_validate(
        {
            "mode": "evidence",
            "obligationId": obligation.metadata.id,
            "dimension": dim.value,
            "status": dim_result.status.value,
            "requiredTypes": list(required),
            "observedEvidenceIds": list(dim_result.observed_evidence_ids),
            "reasons": [item.model_dump(by_alias=True, mode="json") for item in _sorted_reasons(codes)],
        }
    )


def explain_plan_item(item: ProposalItem) -> ExplainPayload:
    detail = planned_verification_detail(item)
    status = detail.gap_status
    if status not in {None, "COVERED", "MISSING", "UNKNOWN"}:
        status = None
    return ExplainPayload.model_validate(
        {
            "mode": "plan_item",
            "obligationId": item.obligation_ref,
            "dimension": detail.dimension,
            "status": status,
            "requiredTypes": [],
            "observedEvidenceIds": [],
            "reasons": [],
            "itemId": item.id,
            "rank": detail.rank,
            "priorityScore": detail.priority_score,
            "suggestedEvidenceType": detail.suggested_evidence_type,
            "missingEvidenceTypes": detail.missing_evidence_types,
        }
    )
