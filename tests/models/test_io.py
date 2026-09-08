from __future__ import annotations

from pathlib import Path

import pytest

from qcov.models.io import ProtocolLoadError, load_evidence, load_policy


def test_load_evidence_reports_schema_error_with_stable_code(tmp_path: Path) -> None:
    invalid = tmp_path / "evidence.yaml"
    invalid.write_text("kind: QualityEvidence\n")

    with pytest.raises(ProtocolLoadError, match="QCOV-SCHEMA-001"):
        load_evidence(invalid)


def test_load_policy_rejects_waiver_expiry_without_timezone(tmp_path: Path) -> None:
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityPolicy
metadata:
  id: release
rules:
  default:
    allowedStatuses: [COVERED]
waivers:
  - obligationRef: QO-001
    reason: temporary exception
    expiresAt: 2026-10-01T00:00:00
"""
    )

    with pytest.raises(ProtocolLoadError, match="timezone-aware"):
        load_policy(policy)


def test_load_mapping_rejects_coverage_producer(tmp_path: Path) -> None:
    from qcov.models.io import load_mapping

    mapping = tmp_path / "mapping.yaml"
    mapping.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: EvidenceMapping
metadata:
  id: bad
defaultTimestamp: 2026-09-08T00:00:00+08:00
mappings:
  - from:
      producer: coverage.py
      identity: src/app.py
    to:
      obligationRef: QO-REFUND-001
      dimension: behavior
      type: line_coverage
"""
    )
    with pytest.raises(ProtocolLoadError, match="QCOV-SCHEMA-001"):
        load_mapping(mapping)
