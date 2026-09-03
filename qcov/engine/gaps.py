"""Pure, explainable calculation of quality evidence gaps."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from qcov.models.protocol import (
    CoverageStatus,
    QualityDimension,
    QualityEvidence,
    TestingObligation,
)


@dataclass(frozen=True)
class DimensionResult:
    """The evidence state of one required quality dimension."""

    dimension: QualityDimension
    required_types: tuple[str, ...]
    status: CoverageStatus
    observed_evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class ObligationResult:
    """An explainable status for one Testing Obligation."""

    obligation_id: str
    status: CoverageStatus
    dimensions: tuple[DimensionResult, ...]

    @property
    def unproven_dimensions(self) -> tuple[DimensionResult, ...]:
        return tuple(item for item in self.dimensions if item.status is not CoverageStatus.COVERED)


def _evaluate_dimension(
    obligation: TestingObligation,
    dimension: QualityDimension,
    required_types: list[str],
    evidence: Sequence[QualityEvidence],
) -> DimensionResult:
    matching = tuple(
        item
        for item in evidence
        if item.obligation.ref == obligation.metadata.id
        and item.evidence.dimension is dimension
        and item.evidence.type in required_types
    )
    observed_ids = tuple(item.metadata.id for item in matching)
    if any(item.execution.status == "passed" for item in matching):
        status = CoverageStatus.COVERED
    elif any(item.execution.status == "unknown" for item in matching):
        status = CoverageStatus.UNKNOWN
    else:
        status = CoverageStatus.MISSING
    return DimensionResult(dimension, tuple(required_types), status, observed_ids)


def _summarize(dimensions: Sequence[DimensionResult]) -> CoverageStatus:
    statuses = {item.status for item in dimensions}
    if statuses == {CoverageStatus.COVERED}:
        return CoverageStatus.COVERED
    if statuses == {CoverageStatus.MISSING}:
        return CoverageStatus.MISSING
    if statuses == {CoverageStatus.UNKNOWN}:
        return CoverageStatus.UNKNOWN
    return CoverageStatus.PARTIAL


def evaluate_obligation(
    obligation: TestingObligation, evidence: Sequence[QualityEvidence]
) -> ObligationResult:
    """Evaluate explicit evidence against an obligation without inference or scoring."""
    dimensions = tuple(
        _evaluate_dimension(obligation, dimension, types, evidence)
        for dimension, types in obligation.required_evidence.items()
    )
    return ObligationResult(obligation.metadata.id, _summarize(dimensions), dimensions)
