"""Pure deterministic quality-policy evaluation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from qcov.engine.gaps import ObligationResult
from qcov.models.protocol import CoverageStatus, PolicyWaiver, QualityPolicy


class PolicyDecision(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class PolicyViolation:
    code: str


@dataclass(frozen=True)
class PolicyResult:
    obligation_id: str
    coverage_status: CoverageStatus
    decision: PolicyDecision
    violations: tuple[PolicyViolation, ...]
    waiver: PolicyWaiver | None


@dataclass(frozen=True)
class PolicyReport:
    policy_id: str
    evaluated_at: datetime
    results: tuple[PolicyResult, ...]


def evaluate_policy(
    results: Sequence[ObligationResult], policy: QualityPolicy, as_of: datetime
) -> PolicyReport:
    """Evaluate immutable coverage facts using a caller-supplied instant."""
    waivers = {waiver.obligation_ref: waiver for waiver in policy.waivers}
    allowed = set(policy.rules.default.allowed_statuses)
    evaluated: list[PolicyResult] = []
    for result in sorted(results, key=lambda item: item.obligation_id):
        waiver = waivers.get(result.obligation_id)
        if result.status in allowed:
            decision = PolicyDecision.WARN if waiver is not None and waiver.expires_at <= as_of else PolicyDecision.PASS
            evaluated.append(PolicyResult(result.obligation_id, result.status, decision, (), waiver))
        elif waiver is not None and waiver.expires_at > as_of:
            evaluated.append(PolicyResult(result.obligation_id, result.status, PolicyDecision.WARN, (), waiver))
        else:
            code = "QCOV-POLICY-002" if waiver is not None else "QCOV-POLICY-001"
            evaluated.append(
                PolicyResult(
                    result.obligation_id,
                    result.status,
                    PolicyDecision.BLOCK,
                    (PolicyViolation(code),),
                    waiver,
                )
            )
    return PolicyReport(policy.metadata.id, as_of, tuple(evaluated))
