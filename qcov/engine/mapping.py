"""Deterministic inventory-to-evidence mapping."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

from qcov.adapters.base import InventoryRecord
from qcov.models.protocol import EvidenceMapping, MappingEntry, QualityEvidence


class MappingConflictError(ValueError):
    """Fatal conflict when mapped evidence ids collide."""

    code = "QCOV-MAP-002"


class MappingDocumentError(ValueError):
    """Fatal conflict when EvidenceMapping document ids collide."""

    code = "QCOV-MAP-007"


@dataclass(frozen=True)
class MappingDiagnostic:
    code: str
    message: str
    mapping_id: str | None = None
    producer: str | None = None
    identity: str | None = None
    artifact_path: str | None = None


@dataclass(frozen=True)
class MappingMaterialization:
    evidence: tuple[QualityEvidence, ...]
    diagnostics: tuple[MappingDiagnostic, ...]
    mapping_ids: tuple[str, ...]


_JUNIT_STATUS = {"passed": "passed", "failed": "failed", "skipped": "skipped"}
_PLAYWRIGHT_STATUS = {
    "passed": "passed",
    "expected": "passed",
    "unexpected": "failed",
    "skipped": "skipped",
    "flaky": "failed",
}
_PRODUCTION_STATUS = {
    "passed": "passed",
    "failed": "failed",
    "skipped": "skipped",
    "unknown": "unknown",
}


def stable_evidence_id(
    producer: str,
    identity: str,
    obligation_ref: str,
    dimension: str,
    evidence_type: str,
) -> str:
    """Deterministic default evidence id locked by tests."""
    token = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    safe_type = re.sub(r"[^A-Za-z0-9._-]+", "_", evidence_type)
    return f"QE-MAP-{producer}-{token}-{obligation_ref}-{dimension}-{safe_type}"


def relative_artifact_path(artifact_path: str, config_dir: Path) -> tuple[str, bool]:
    """Return a stable relative path, or basename when relativization fails."""
    path = Path(artifact_path)
    try:
        relative = path.resolve().relative_to(config_dir.resolve())
        return PurePosixPath(relative.as_posix()).as_posix(), False
    except ValueError:
        return path.name, True


def _translate_status(producer: str, status: str) -> tuple[str, bool]:
    tables = {
        "junit": _JUNIT_STATUS,
        "playwright": _PLAYWRIGHT_STATUS,
        "production-observation": _PRODUCTION_STATUS,
    }
    table = tables.get(producer, {})
    if status in table:
        return table[status], False
    return "unknown", True


def _execution_timestamp(record: InventoryRecord, entry: MappingEntry, mapping: EvidenceMapping) -> datetime:
    if record.producer == "production-observation":
        return datetime.fromisoformat(record.metadata["timestamp"])
    return entry.timestamp or mapping.default_timestamp


def identity_matches(pattern: str, identity: str) -> bool:
    """Exact match, or single trailing ``*`` suffix wildcard (one star only)."""
    if "*" not in pattern:
        return identity == pattern
    if not pattern.endswith("*") or pattern.count("*") != 1:
        return identity == pattern
    prefix = pattern[:-1]
    return identity.startswith(prefix)


def _entry_evidence_id(entry: MappingEntry, matched_identity: str | None = None) -> str:
    if entry.to.evidence_id is not None:
        return entry.to.evidence_id
    identity = matched_identity if matched_identity is not None else entry.from_.identity
    return stable_evidence_id(
        entry.from_.producer,
        identity,
        entry.to.obligation_ref,
        entry.to.dimension.value,
        entry.to.type,
    )


def _require_unique_mapping_ids(mappings: Sequence[EvidenceMapping]) -> tuple[str, ...]:
    id_counts: dict[str, int] = {}
    for mapping in mappings:
        id_counts[mapping.metadata.id] = id_counts.get(mapping.metadata.id, 0) + 1
    duplicates = sorted(mapping_id for mapping_id, count in id_counts.items() if count > 1)
    if duplicates:
        raise MappingDocumentError(
            f"{MappingDocumentError.code}: duplicate mapping metadata.id: {duplicates}"
        )
    return tuple(sorted(item.metadata.id for item in mappings))


def apply_mappings(
    records: Sequence[InventoryRecord],
    mappings: Sequence[EvidenceMapping],
    config_dir: Path,
    authored_ids: set[str] | None = None,
) -> MappingMaterialization:
    """Materialize QualityEvidence from inventory using explicit mappings."""
    authored = authored_ids or set()
    diagnostics: list[MappingDiagnostic] = []
    evidence: list[QualityEvidence] = []
    seen_ids: set[str] = set(authored)
    mapping_ids = _require_unique_mapping_ids(mappings)

    for mapping in mappings:
        for entry in mapping.mappings:
            matches = [
                record
                for record in records
                if record.producer == entry.from_.producer
                and identity_matches(entry.from_.identity, record.identity)
            ]
            if not matches:
                diagnostics.append(
                    MappingDiagnostic(
                        "QCOV-MAP-001",
                        "inventory identity not found",
                        mapping.metadata.id,
                        entry.from_.producer,
                        entry.from_.identity,
                    )
                )
                continue
            if len(matches) > 1:
                diagnostics.append(
                    MappingDiagnostic(
                        "QCOV-MAP-005",
                        "ambiguous inventory identity",
                        mapping.metadata.id,
                        entry.from_.producer,
                        entry.from_.identity,
                    )
                )
                continue

            record = matches[0]
            evidence_id = _entry_evidence_id(entry, matched_identity=record.identity)
            if evidence_id in seen_ids:
                raise MappingConflictError(
                    f"{MappingConflictError.code}: duplicate evidence id: {evidence_id}"
                )
            seen_ids.add(evidence_id)

            status, unknown_status = _translate_status(record.producer, record.status)
            if unknown_status:
                diagnostics.append(
                    MappingDiagnostic(
                        "QCOV-MAP-003",
                        f"unrecognized inventory status: {record.status}",
                        mapping.metadata.id,
                        entry.from_.producer,
                        entry.from_.identity,
                    )
                )

            artifact, degraded = relative_artifact_path(record.artifact_path, config_dir)
            if degraded:
                diagnostics.append(
                    MappingDiagnostic(
                        "QCOV-MAP-006",
                        "artifact path could not be relativized; using basename",
                        mapping.metadata.id,
                        entry.from_.producer,
                        entry.from_.identity,
                        artifact_path=record.artifact_path,
                    )
                )

            timestamp = _execution_timestamp(record, entry, mapping)
            evidence.append(
                QualityEvidence.model_validate(
                    {
                        "apiVersion": "qcov.dev/v1alpha1",
                        "kind": "QualityEvidence",
                        "metadata": {"id": evidence_id},
                        "obligation": {"ref": entry.to.obligation_ref},
                        "evidence": {
                            "dimension": entry.to.dimension.value,
                            "type": entry.to.type,
                        },
                        "producer": {"name": record.producer, "adapter": "qcov-mapping"},
                        "execution": {"status": status, "timestamp": timestamp.isoformat()},
                        "artifact": {"path": artifact},
                        "confidence": {"deterministic": True, "reproducible": True},
                    }
                )
            )

    diagnostics.sort(
        key=lambda item: (
            item.code,
            item.message,
            item.mapping_id or "",
            item.identity or "",
            item.artifact_path or "",
        )
    )
    evidence.sort(key=lambda item: item.metadata.id)
    return MappingMaterialization(tuple(evidence), tuple(diagnostics), mapping_ids)
