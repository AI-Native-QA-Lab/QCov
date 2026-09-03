from pathlib import Path

from qcov.engine.gaps import evaluate_obligation
from qcov.models.io import load_evidence, load_obligation
from qcov.models.protocol import CoverageStatus

ROOT = Path(__file__).parents[2]


def test_refund_fixture_exposes_intended_gaps() -> None:
    obligation = load_obligation(ROOT / "examples/refund/obligation.yaml")
    evidence = [
        load_evidence(ROOT / "examples/refund/evidence/behavior.yaml"),
        load_evidence(ROOT / "examples/refund/evidence/boundary.yaml"),
        load_evidence(ROOT / "examples/refund/evidence/data.yaml"),
    ]
    result = evaluate_obligation(obligation, evidence)

    assert result.status is CoverageStatus.PARTIAL
    assert {item.dimension.value for item in result.unproven_dimensions} == {
        "concurrency",
        "idempotency",
        "production",
    }
