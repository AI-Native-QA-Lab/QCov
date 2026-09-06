"""Pure comparison of two evaluated Git protocol snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from qcov.engine.gaps import ObligationResult, evaluate_obligation
from qcov.engine.git_snapshots import Snapshot


class ChangeKind(StrEnum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"


@dataclass(frozen=True)
class ObligationDelta:
    obligation_id: str
    kind: ChangeKind
    before: ObligationResult | None
    after: ObligationResult | None
    changed_evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class DeltaReport:
    base_commit: str
    head_commit: str
    obligations: tuple[ObligationDelta, ...]


def compare_snapshots(base: Snapshot, head: Snapshot) -> DeltaReport:
    deltas: list[ObligationDelta] = []
    for identifier in sorted(set(base.obligations) | set(head.obligations)):
        before_obligation = base.obligations.get(identifier)
        after_obligation = head.obligations.get(identifier)
        before = (
            evaluate_obligation(before_obligation, tuple(base.evidence.values()))
            if before_obligation is not None
            else None
        )
        after = (
            evaluate_obligation(after_obligation, tuple(head.evidence.values()))
            if after_obligation is not None
            else None
        )
        before_evidence = {
            evidence_id: item
            for evidence_id, item in base.evidence.items()
            if item.obligation.ref == identifier
        }
        after_evidence = {
            evidence_id: item
            for evidence_id, item in head.evidence.items()
            if item.obligation.ref == identifier
        }
        changed_evidence_ids = tuple(
            evidence_id
            for evidence_id in sorted(set(before_evidence) | set(after_evidence))
            if before_evidence.get(evidence_id) != after_evidence.get(evidence_id)
        )
        if before_obligation is None:
            kind = ChangeKind.ADDED
        elif after_obligation is None:
            kind = ChangeKind.REMOVED
        elif before_obligation != after_obligation or changed_evidence_ids:
            kind = ChangeKind.MODIFIED
        else:
            kind = ChangeKind.UNCHANGED
        deltas.append(ObligationDelta(identifier, kind, before, after, changed_evidence_ids))
    return DeltaReport(base.commit, head.commit, tuple(deltas))
