from pathlib import Path

from qcov.adapters.production_observation import ProductionObservationAdapter


def test_production_observation_adapter_retains_identity_status_and_timestamp(tmp_path: Path) -> None:
    artifact = tmp_path / "production.yaml"
    artifact.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: ProductionObservationReport
metadata: {id: checkout-release}
observations:
  - id: availability
    category: runtime
    status: passed
    timestamp: 2026-09-11T00:00:00+08:00
    attributes: {service: checkout}
"""
    )

    result = ProductionObservationAdapter().scan(artifact)

    assert [(item.identity, item.status, item.metadata) for item in result.records] == [
        (
            "checkout-release::availability",
            "passed",
            {
                "category": "runtime",
                "timestamp": "2026-09-11T00:00:00+08:00",
                "service": "checkout",
            },
        )
    ]
    assert result.diagnostics == ()


def test_production_observation_adapter_reports_invalid_document_without_records(tmp_path: Path) -> None:
    artifact = tmp_path / "production.yaml"
    artifact.write_text("kind: ProductionObservationReport\n")

    result = ProductionObservationAdapter().scan(artifact)

    assert result.records == ()
    assert result.diagnostics[0].code == "QCOV-SCAN-001"


def test_production_observation_adapter_does_not_allow_attributes_to_override_timestamp(tmp_path: Path) -> None:
    artifact = tmp_path / "production.yaml"
    artifact.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: ProductionObservationReport
metadata: {id: checkout-release}
observations:
  - id: availability
    category: runtime
    status: passed
    timestamp: 2026-09-11T00:00:00+08:00
    attributes: {timestamp: invalid, category: forged}
"""
    )

    result = ProductionObservationAdapter().scan(artifact)

    assert result.records[0].metadata["timestamp"] == "2026-09-11T00:00:00+08:00"
    assert result.records[0].metadata["category"] == "runtime"
