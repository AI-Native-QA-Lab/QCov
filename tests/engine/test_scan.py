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
        ("pytest-marker", 0),
    ]


def test_scan_project_retains_missing_configured_artifact_as_diagnostic(tmp_path: Path) -> None:
    config = tmp_path / "qcov.yaml"
    config.write_text("apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\nscan:\n  junit: [missing.xml]\n")

    report = scan_project(tmp_path, config)

    assert report.diagnostics[0].code == "QCOV-SCAN-001"
