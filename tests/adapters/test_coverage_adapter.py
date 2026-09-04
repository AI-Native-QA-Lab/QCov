from pathlib import Path

from qcov.adapters.coverage import CoverageAdapter


def write_coverage(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "coverage.xml"
    path.write_text(f'<coverage line-rate="0.75"><packages>{body}</packages></coverage>')
    return path


def test_coverage_scan_reads_class_and_package_line_rates(tmp_path: Path) -> None:
    report = write_coverage(
        tmp_path,
        '<package name="qcov" line-rate="0.80"><classes>'
        '<class name="qcov.engine.gaps" filename="qcov/engine/gaps.py" line-rate="0.90" />'
        '</classes></package>',
    )

    result = CoverageAdapter().scan(report)

    assert result.records[0].identity == "qcov/engine/gaps.py"
    assert result.records[0].metadata["lineRate"] == "0.90"
    assert result.records[0].producer == "coverage.py"


def test_coverage_scan_reports_malformed_xml_as_diagnostic(tmp_path: Path) -> None:
    report = tmp_path / "coverage.xml"
    report.write_text("<coverage>")

    result = CoverageAdapter().scan(report)

    assert result.records == ()
    assert result.diagnostics[0].code == "QCOV-SCAN-001"
