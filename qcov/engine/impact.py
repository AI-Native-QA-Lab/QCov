"""Pure, deterministic Change to Obligation Impact evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import PurePosixPath
from typing import Literal

from qcov.engine.gaps import ObligationResult, evaluate_obligation
from qcov.engine.git_snapshots import Snapshot
from qcov.models.impact import QualityImpactConfig
from qcov.models.protocol import CoverageStatus


class ImpactInputError(ValueError):
    """Invalid user input for deterministic local impact evaluation."""

    code = "QCOV-IMPACT-001"


@dataclass(frozen=True)
class ImpactDiagnostic:
    code: str
    message: str
    severity: Literal["error", "warning", "info"]
    path: str | None = None


@dataclass(frozen=True)
class GapItem:
    obligation_id: str
    status: str
    missing_dimensions: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {"obligationId": self.obligation_id, "status": self.status, "missingDimensions": list(self.missing_dimensions)}


@dataclass(frozen=True)
class ImpactReport:
    changed_files: tuple[str, ...]
    affected_obligations: tuple[str, ...]
    new_gaps: tuple[GapItem, ...]
    resolved_gaps: tuple[GapItem, ...]
    diagnostics: tuple[ImpactDiagnostic, ...]


@dataclass(frozen=True)
class AffectedReport:
    """Current key gaps for obligations selected by explicit changed files."""

    changed_files: tuple[str, ...]
    affected_obligations: tuple[str, ...]
    diagnostics: tuple[ImpactDiagnostic, ...]
    key_gaps: tuple[GapItem, ...]


def affected_report(
    impact: ImpactReport, results: tuple[ObligationResult, ...]
) -> AffectedReport:
    """Keep non-covered current results for explicitly affected obligations only."""
    by_id = {item.obligation_id: item for item in results}
    key_gaps = tuple(
        sorted(
            (
                GapItem(
                    item.obligation_id,
                    item.status.value,
                    tuple(sorted(dimension.dimension.value for dimension in item.unproven_dimensions)),
                )
                for obligation_id in impact.affected_obligations
                if (item := by_id.get(obligation_id)) is not None
                and item.status is not CoverageStatus.COVERED
            ),
            key=lambda item: (item.obligation_id, item.status, item.missing_dimensions),
        )
    )
    return AffectedReport(
        impact.changed_files,
        impact.affected_obligations,
        tuple(item for item in impact.diagnostics if item.code != "QCOV-IMPACT-004"),
        key_gaps,
    )


def _safe_path(value: str) -> PurePosixPath:
    candidate = PurePosixPath(value)
    if not value or candidate.is_absolute() or ".." in candidate.parts or value == ".":
        raise ImpactInputError(f"{ImpactInputError.code}: unsafe repository path: {value!r}")
    return candidate


def _matches(pattern: PurePosixPath, relative: PurePosixPath) -> bool:
    pattern_parts = pattern.parts
    path_parts = relative.parts

    def matches_at(pattern_index: int, path_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        part = pattern_parts[pattern_index]
        if part == "**":
            return any(matches_at(pattern_index + 1, index) for index in range(path_index, len(path_parts) + 1))
        return (
            path_index < len(path_parts)
            and fnmatchcase(path_parts[path_index], part)
            and matches_at(pattern_index + 1, path_index + 1)
        )

    return matches_at(0, 0)


def direct_impact(
    config: QualityImpactConfig,
    changed_files: tuple[str, ...],
    *,
    known_obligation_ids: set[str] | None = None,
) -> ImpactReport:
    """Evaluate explicit changed files without inventing a gap delta."""
    if not changed_files:
        raise ImpactInputError(f"{ImpactInputError.code}: provide at least one changed file")
    paths = tuple(sorted({str(_safe_path(item)) for item in changed_files}))
    matched_obligations: set[str] = set()
    diagnostics: list[ImpactDiagnostic] = []
    compiled = tuple(
        (tuple(_safe_path(pattern) for pattern in mapping.paths), tuple(mapping.obligations))
        for mapping in config.mappings
    )
    if known_obligation_ids is not None:
        unknown = sorted(
            {
                obligation
                for _patterns, mapping_obligations in compiled
                for obligation in mapping_obligations
                if obligation not in known_obligation_ids
            }
        )
        if unknown:
            raise ImpactInputError(
                "QCOV-IMPACT-003: impact mapping references unknown obligation: "
                + ", ".join(unknown)
            )
    for raw_path in paths:
        path = PurePosixPath(raw_path)
        obligations = {
            obligation
            for patterns, mapping_obligations in compiled
            if any(_matches(pattern, path) for pattern in patterns)
            for obligation in mapping_obligations
        }
        if obligations:
            matched_obligations.update(obligations)
        else:
            diagnostics.append(
                ImpactDiagnostic(
                    "QCOV-IMPACT-002",
                    "changed file matched no impact mapping",
                    "warning",
                    raw_path,
                )
            )
    diagnostics.append(
        ImpactDiagnostic("QCOV-IMPACT-004", "gap delta not assessed", "info")
    )
    diagnostics.sort(key=lambda item: (item.code, item.message, item.path or ""))
    return ImpactReport(paths, tuple(sorted(matched_obligations)), (), (), tuple(diagnostics))


def snapshot_impact(config: QualityImpactConfig, changed_files: tuple[str, ...], base: Snapshot, head: Snapshot) -> ImpactReport:
    """Evaluate affected obligations and their deterministic Gap delta across local snapshots."""
    direct = direct_impact(config, changed_files, known_obligation_ids=set(base.obligations) | set(head.obligations))
    diagnostics = tuple(item for item in direct.diagnostics if item.code != "QCOV-IMPACT-004")
    def result(snapshot: Snapshot, obligation_id: str) -> ObligationResult | None:
        obligation = snapshot.obligations.get(obligation_id)
        return evaluate_obligation(obligation, tuple(snapshot.evidence.values())) if obligation else None
    def gap(item: ObligationResult) -> GapItem:
        return GapItem(item.obligation_id, item.status.value, tuple(sorted(part.dimension.value for part in item.unproven_dimensions)))
    new: list[GapItem] = []
    resolved: list[GapItem] = []
    for obligation_id in direct.affected_obligations:
        before, after = result(base, obligation_id), result(head, obligation_id)
        if after is not None and after.status is not CoverageStatus.COVERED and (before is None or before.status is CoverageStatus.COVERED):
            new.append(gap(after))
        if before is not None and after is not None and before.status is not CoverageStatus.COVERED and after.status is CoverageStatus.COVERED:
            resolved.append(gap(before))
    return ImpactReport(direct.changed_files, direct.affected_obligations, tuple(sorted(new, key=lambda item: (item.obligation_id, item.status, item.missing_dimensions))), tuple(sorted(resolved, key=lambda item: (item.obligation_id, item.status, item.missing_dimensions))), diagnostics)
