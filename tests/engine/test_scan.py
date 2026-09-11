from pathlib import Path

from qcov.engine.scan import scan_project


def test_scan_project_collects_configured_junit_and_coverage_inventory(tmp_path: Path) -> None:
    (tmp_path / "junit.xml").write_text('<testsuite><testcase name="works" /></testsuite>')
    (tmp_path / "coverage.xml").write_text(
        '<coverage><packages><package><classes><class filename="app.py" line-rate="1.0" />'
        '</classes></package></packages></coverage>'
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        "scan:\n  junit: [junit.xml]\n  coverage: [coverage.xml]\n"
    )

    report = scan_project(tmp_path, config)

    assert [(item.adapter, item.record_count) for item in report.adapters] == [
        ("coverage.py", 1),
        ("junit", 1),
        ("lcov", 0),
        ("playwright", 0),
        ("production-observation", 0),
        ("pytest-marker", 0),
    ]
    assert len(report.records) == 2
    assert {record.producer for record in report.records} == {"junit", "coverage.py"}


def test_scan_project_retains_missing_configured_artifact_as_diagnostic(tmp_path: Path) -> None:
    config = tmp_path / "qcov.yaml"
    config.write_text("apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\nscan:\n  junit: [missing.xml]\n")

    report = scan_project(tmp_path, config)

    assert report.diagnostics[0].code == "QCOV-SCAN-001"


def test_scan_project_reports_pytest_marker_files_and_records(tmp_path: Path) -> None:
    (tmp_path / "test_refund.py").write_text(
        'import pytest\n\n@pytest.mark.qcov("QO-REFUND-001")\ndef test_refund():\n    pass\n'
    )
    config = tmp_path / "qcov.yaml"
    config.write_text("apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n")

    report = scan_project(tmp_path, config)

    pytest = next(item for item in report.adapters if item.adapter == "pytest-marker")
    assert pytest.files == (str(tmp_path / "test_refund.py"),)
    assert pytest.record_count == 1


def test_scan_project_uses_deterministic_cross_language_adapter_order(tmp_path: Path) -> None:
    config = tmp_path / "qcov.yaml"
    config.write_text("apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n")

    report = scan_project(tmp_path, config)

    assert [item.adapter for item in report.adapters] == [
        "coverage.py", "junit", "lcov", "playwright", "production-observation", "pytest-marker"
    ]


def test_scan_project_collects_configured_production_inventory(tmp_path: Path) -> None:
    (tmp_path / "production.yaml").write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: ProductionObservationReport
metadata: {id: checkout-release}
observations:
  - id: availability
    category: runtime
    status: passed
    timestamp: 2026-09-11T00:00:00+08:00
"""
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        "scan:\n  production: [production.yaml]\n"
    )

    report = scan_project(tmp_path, config)

    production = next(item for item in report.adapters if item.adapter == "production-observation")
    assert production.record_count == 1
    assert report.records[-1].identity == "checkout-release::availability"
