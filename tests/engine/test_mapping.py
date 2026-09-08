from __future__ import annotations

from pathlib import Path

import pytest

from qcov.adapters.base import InventoryRecord
from qcov.engine.mapping import MappingConflictError, apply_mappings, stable_evidence_id
from qcov.models.protocol import EvidenceMapping

MAPPING = EvidenceMapping.model_validate(
    {
        "apiVersion": "qcov.dev/v1alpha1",
        "kind": "EvidenceMapping",
        "metadata": {"id": "refund-import-mapping"},
        "defaultTimestamp": "2026-09-08T00:00:00+08:00",
        "mappings": [
            {
                "from": {"producer": "junit", "identity": "refund.api::refund_is_accepted"},
                "to": {
                    "obligationRef": "QO-REFUND-001",
                    "dimension": "behavior",
                    "type": "api_test",
                },
            }
        ],
    }
)


def test_apply_mappings_translates_junit_passed(tmp_path: Path) -> None:
    artifact = tmp_path / "junit.xml"
    artifact.write_text("<ok/>")
    result = apply_mappings(
        [
            InventoryRecord(
                "junit", "refund.api::refund_is_accepted", "passed", str(artifact), {}
            )
        ],
        [MAPPING],
        tmp_path,
    )

    assert len(result.evidence) == 1
    evidence = result.evidence[0]
    assert evidence.execution.status == "passed"
    assert evidence.producer.adapter == "qcov-mapping"
    assert evidence.artifact.path == "junit.xml"
    assert evidence.metadata.id == stable_evidence_id(
        "junit", "refund.api::refund_is_accepted", "QO-REFUND-001", "behavior", "api_test"
    )


def test_apply_mappings_reports_missing_identity(tmp_path: Path) -> None:
    result = apply_mappings([], [MAPPING], tmp_path)
    assert result.evidence == ()
    assert result.diagnostics[0].code == "QCOV-MAP-001"


def test_apply_mappings_reports_ambiguous_identity(tmp_path: Path) -> None:
    artifact = tmp_path / "junit.xml"
    artifact.write_text("<ok/>")
    duplicate = InventoryRecord(
        "junit", "refund.api::refund_is_accepted", "passed", str(artifact), {}
    )
    result = apply_mappings([duplicate, duplicate], [MAPPING], tmp_path)
    assert result.evidence == ()
    assert result.diagnostics[0].code == "QCOV-MAP-005"


def test_apply_mappings_rejects_duplicate_evidence_ids(tmp_path: Path) -> None:
    artifact = tmp_path / "junit.xml"
    artifact.write_text("<ok/>")
    with pytest.raises(MappingConflictError, match="QCOV-MAP-002"):
        apply_mappings(
            [
                InventoryRecord(
                    "junit", "refund.api::refund_is_accepted", "passed", str(artifact), {}
                )
            ],
            [MAPPING],
            tmp_path,
            authored_ids={
                stable_evidence_id(
                    "junit",
                    "refund.api::refund_is_accepted",
                    "QO-REFUND-001",
                    "behavior",
                    "api_test",
                )
            },
        )


def test_apply_mappings_unknown_status_emits_map_003(tmp_path: Path) -> None:
    artifact = tmp_path / "junit.xml"
    artifact.write_text("<ok/>")
    result = apply_mappings(
        [
            InventoryRecord(
                "junit", "refund.api::refund_is_accepted", "weird", str(artifact), {}
            )
        ],
        [MAPPING],
        tmp_path,
    )
    assert result.evidence[0].execution.status == "unknown"
    assert result.diagnostics[0].code == "QCOV-MAP-003"


def test_apply_mappings_emits_map_006_when_path_cannot_relativize(tmp_path: Path) -> None:
    outside = Path("/tmp/qcov-outside-artifact.xml")
    result = apply_mappings(
        [
            InventoryRecord(
                "junit", "refund.api::refund_is_accepted", "passed", str(outside), {}
            )
        ],
        [MAPPING],
        tmp_path,
    )
    assert result.evidence[0].artifact.path == "qcov-outside-artifact.xml"
    assert result.diagnostics[0].code == "QCOV-MAP-006"


def test_duplicate_mapping_document_ids_use_map_007(tmp_path: Path) -> None:
    from qcov.engine.mapping import MappingDocumentError

    artifact = tmp_path / "junit.xml"
    artifact.write_text("<ok/>")
    with pytest.raises(MappingDocumentError, match="QCOV-MAP-007"):
        apply_mappings(
            [
                InventoryRecord(
                    "junit", "refund.api::refund_is_accepted", "passed", str(artifact), {}
                )
            ],
            [MAPPING, MAPPING],
            tmp_path,
        )


def test_playwright_flaky_becomes_failed(tmp_path: Path) -> None:
    mapping = EvidenceMapping.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "EvidenceMapping",
            "metadata": {"id": "pw"},
            "defaultTimestamp": "2026-09-08T00:00:00+08:00",
            "mappings": [
                {
                    "from": {
                        "producer": "playwright",
                        "identity": "tests/refund.spec.ts::refund > shows confirmation [chromium]",
                    },
                    "to": {
                        "obligationRef": "QO-REFUND-001",
                        "dimension": "behavior",
                        "type": "e2e_test",
                        "evidenceId": "QE-MAP-E2E",
                    },
                }
            ],
        }
    )
    artifact = tmp_path / "playwright.json"
    artifact.write_text("{}")
    result = apply_mappings(
        [
            InventoryRecord(
                "playwright",
                "tests/refund.spec.ts::refund > shows confirmation [chromium]",
                "flaky",
                str(artifact),
                {},
            )
        ],
        [mapping],
        tmp_path,
    )
    assert result.evidence[0].execution.status == "failed"
