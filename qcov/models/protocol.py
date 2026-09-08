"""Strict models for the QCov v1alpha1 protocol."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProtocolModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CoverageStatus(StrEnum):
    COVERED = "COVERED"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class QualityDimension(StrEnum):
    BEHAVIOR = "behavior"
    BOUNDARY = "boundary"
    DATA = "data"
    CONCURRENCY = "concurrency"
    IDEMPOTENCY = "idempotency"
    PRODUCTION = "production"
    SECURITY = "security"
    FAULT = "fault"
    INTEGRATION = "integration"


class LocalizedText(ProtocolModel):
    en: str
    zh_cn: str = Field(alias="zh-CN")


class ObligationMetadata(ProtocolModel):
    id: str
    title: LocalizedText


class SourceRef(ProtocolModel):
    type: str
    ref: str


class Risk(ProtocolModel):
    domain: str
    severity: str


class Invariant(ProtocolModel):
    id: str
    expression: str


class TestingObligation(ProtocolModel):
    __test__ = False
    api_version: Literal["qcov.dev/v1alpha1"] = Field(alias="apiVersion")
    kind: Literal["TestingObligation"]
    metadata: ObligationMetadata
    source: SourceRef
    risk: Risk
    invariants: list[Invariant] = Field(default_factory=list)
    required_evidence: dict[QualityDimension, list[str]] = Field(alias="requiredEvidence")


class EvidenceMetadata(ProtocolModel):
    id: str


class ObligationRef(ProtocolModel):
    ref: str


class EvidenceDescriptor(ProtocolModel):
    dimension: QualityDimension
    type: str


class Producer(ProtocolModel):
    name: str
    adapter: str | None = None
    language: str | None = None


class Execution(ProtocolModel):
    status: Literal["passed", "failed", "skipped", "unknown"]
    timestamp: datetime


class Artifact(ProtocolModel):
    path: str


class Confidence(ProtocolModel):
    deterministic: bool
    reproducible: bool


class QualityEvidence(ProtocolModel):
    api_version: Literal["qcov.dev/v1alpha1"] = Field(alias="apiVersion")
    kind: Literal["QualityEvidence"]
    metadata: EvidenceMetadata
    obligation: ObligationRef
    evidence: EvidenceDescriptor
    producer: Producer
    execution: Execution
    artifact: Artifact
    confidence: Confidence


class DefaultPolicyRule(ProtocolModel):
    allowed_statuses: list[CoverageStatus] = Field(alias="allowedStatuses", min_length=1)


class PolicyRules(ProtocolModel):
    default: DefaultPolicyRule


class PolicyWaiver(ProtocolModel):
    obligation_ref: str = Field(alias="obligationRef", min_length=1)
    reason: str = Field(min_length=1)
    expires_at: datetime = Field(alias="expiresAt")
    approved_by: str | None = Field(default=None, alias="approvedBy")

    @field_validator("expires_at")
    @classmethod
    def expiry_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("expiresAt must be timezone-aware")
        return value


class QualityPolicy(ProtocolModel):
    api_version: Literal["qcov.dev/v1alpha1"] = Field(alias="apiVersion")
    kind: Literal["QualityPolicy"]
    metadata: EvidenceMetadata
    rules: PolicyRules
    waivers: list[PolicyWaiver] = Field(default_factory=list)

    @model_validator(mode="after")
    def waiver_obligation_refs_must_be_unique(self) -> QualityPolicy:
        refs = [waiver.obligation_ref for waiver in self.waivers]
        if len(refs) != len(set(refs)):
            raise ValueError("duplicate waiver obligation reference")
        return self
