import pytest

from qcov.engine.impact import ImpactInputError, direct_impact
from qcov.models.impact import QualityImpactConfig


def _config() -> QualityImpactConfig:
    return QualityImpactConfig.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityImpactConfig",
            "mappings": [
                {
                    "id": "refund",
                    "paths": ["src/refund/**"],
                    "obligations": ["QO-REFUND-002", "QO-REFUND-001"],
                }
            ],
        }
    )


def test_direct_impact_sorts_paths_deduplicates_obligations_and_marks_delta_unassessed() -> None:
    report = direct_impact(
        _config(),
        ("src/refund/b.py", "src/refund/a.py", "src/refund/a.py"),
    )

    assert report.changed_files == ("src/refund/a.py", "src/refund/b.py")
    assert report.affected_obligations == ("QO-REFUND-001", "QO-REFUND-002")
    assert report.new_gaps == ()
    assert report.resolved_gaps == ()
    assert report.diagnostics[0].code == "QCOV-IMPACT-004"
    assert report.diagnostics[0].severity == "info"


def test_direct_impact_reports_unmatched_file_as_warning() -> None:
    report = direct_impact(_config(), ("src/other.py",))

    assert report.affected_obligations == ()
    assert report.diagnostics[0].code == "QCOV-IMPACT-002"
    assert report.diagnostics[0].severity == "warning"
    assert report.diagnostics[1].code == "QCOV-IMPACT-004"


@pytest.mark.parametrize("changed_file", ("/src/refund/a.py", "../src/refund/a.py", ""))
def test_direct_impact_rejects_unsafe_repository_path(changed_file: str) -> None:
    with pytest.raises(ImpactInputError, match="QCOV-IMPACT-001"):
        direct_impact(_config(), (changed_file,))
