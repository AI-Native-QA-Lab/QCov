"""Stable agent-facing JSON contract models (Iteration 7)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, model_validator

from qcov.models.protocol import LocalizedText, ProtocolModel

CONTRACT_VERSION = "qcov.agent/v1"

ReasonCode = Literal[
    "ALREADY_COVERED",
    "DIMENSION_MISMATCH",
    "NO_EVIDENCE_FOR_OBLIGATION",
    "OBLIGATION_REF_MISMATCH",
    "STATUS_NOT_PASSED",
    "STATUS_UNKNOWN",
    "TYPE_NOT_REQUIRED",
]


class ReasonItem(ProtocolModel):
    code: ReasonCode
    summary: LocalizedText


class ExplainPayload(ProtocolModel):
    mode: Literal["gap", "plan_item", "evidence"]
    obligation_id: str | None = Field(default=None, alias="obligationId")
    dimension: str | None = None
    status: Literal["COVERED", "MISSING", "UNKNOWN"] | None = None
    required_types: list[str] = Field(default_factory=list, alias="requiredTypes")
    observed_evidence_ids: list[str] = Field(default_factory=list, alias="observedEvidenceIds")
    reasons: list[ReasonItem] = Field(default_factory=list)
    item_id: str | None = Field(default=None, alias="itemId")
    rank: int | None = None
    priority_score: int | None = Field(default=None, alias="priorityScore")
    suggested_evidence_type: str | None = Field(default=None, alias="suggestedEvidenceType")
    missing_evidence_types: list[str] = Field(
        default_factory=list, alias="missingEvidenceTypes"
    )


class NextItem(ProtocolModel):
    id: str = Field(min_length=1)
    obligation_ref: str = Field(alias="obligationRef", min_length=1)
    dimension: str
    suggested_evidence_type: str | None = Field(default=None, alias="suggestedEvidenceType")
    rank: int
    priority_score: int = Field(alias="priorityScore")


class NextPayload(ProtocolModel):
    source: Literal["plan_file", "evaluation"]
    limit: int
    items: list[NextItem] = Field(default_factory=list)


class ValidateFileResult(ProtocolModel):
    path: str
    valid_for_load: bool = Field(alias="validForLoad")
    evidence_id: str | None = Field(default=None, alias="evidenceId")
    error: str | None = None


class ValidatePayload(ProtocolModel):
    files: list[ValidateFileResult] = Field(default_factory=list)
    all_valid_for_load: bool = Field(alias="allValidForLoad")
    disclaimer: LocalizedText


class AgentEnvelope(ProtocolModel):
    contract_version: Literal["qcov.agent/v1"] = Field(alias="contractVersion")
    command: Literal["explain", "agent.next", "agent.validate_evidence"]
    payload: ExplainPayload | NextPayload | ValidatePayload

    @model_validator(mode="before")
    @classmethod
    def _coerce_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        command = data.get("command")
        payload = data.get("payload")
        if not isinstance(payload, dict):
            return data
        if command == "explain":
            return {**data, "payload": ExplainPayload.model_validate(payload)}
        if command == "agent.next":
            return {**data, "payload": NextPayload.model_validate(payload)}
        if command == "agent.validate_evidence":
            return {**data, "payload": ValidatePayload.model_validate(payload)}
        return data
