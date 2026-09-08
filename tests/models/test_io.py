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


def test_load_evidence_rejects_quality_proposal_kind(tmp_path: Path) -> None:
    path = tmp_path / "proposal.yaml"
    path.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityProposal
metadata:
  id: QP-1
  createdAt: 2026-09-08T12:00:00+08:00
proposal:
  type: obligation_suggest
  status: draft
source:
  kind: requirements
  refs: []
provider:
  name: offline
items: []
"""
    )
    with pytest.raises(ProtocolLoadError, match="QCOV-SCHEMA-001"):
        load_evidence(path)


def test_load_proposal_accepts_draft(tmp_path: Path) -> None:
    from qcov.models.io import load_proposal

    path = tmp_path / "proposal.yaml"
    path.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityProposal
metadata:
  id: QP-1
  createdAt: 2026-09-08T12:00:00+08:00
proposal:
  type: change_risk
  status: draft
source:
  kind: local_diff
  refs: [HEAD~1, HEAD]
provider:
  name: offline
items:
  - id: item-1
    kind: affected_obligation
    obligationRef: QO-REFUND-001
    summary:
      en: Affected refund obligation
      zh-CN: 受影响的退款义务
    detail: {}
"""
    )
    proposal = load_proposal(path)
    assert proposal.proposal.type == "change_risk"
    assert proposal.items[0].kind == "affected_obligation"


def test_load_proposal_rejects_invalid_with_proposal_001(tmp_path: Path) -> None:
    from qcov.models.errors import ProposalInputError
    from qcov.models.io import load_proposal

    path = tmp_path / "bad.yaml"
    path.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityProposal
metadata:
  id: QP-1
  createdAt: 2026-09-08T12:00:00+08:00
proposal:
  type: obligation_suggest
  status: approved
source:
  kind: requirements
  refs: []
provider:
  name: offline
items: []
"""
    )
    with pytest.raises(ProposalInputError, match="QCOV-PROPOSAL-001"):
        load_proposal(path)
