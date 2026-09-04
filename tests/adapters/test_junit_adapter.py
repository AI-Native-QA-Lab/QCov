from pathlib import Path

from qcov.adapters.junit import JUnitAdapter


def write_junit(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "junit.xml"
    path.write_text(f'<testsuite name="billing">{body}</testsuite>')
    return path


def test_junit_scan_maps_outcomes_without_creating_quality_evidence(tmp_path: Path) -> None:
    report = write_junit(
        tmp_path,
        '<testcase classname="billing.refund" name="passes" />'
        '<testcase classname="billing.refund" name="fails"><failure /></testcase>'
        '<testcase classname="billing.refund" name="errors"><error /></testcase>'
        '<testcase classname="billing.refund" name="skips"><skipped /></testcase>',
    )

    result = JUnitAdapter().scan(report)

    assert [record.status for record in result.records] == ["passed", "failed", "failed", "skipped"]
    assert result.records[0].identity == "billing.refund::passes"
    assert not hasattr(result.records[0], "obligation")


def test_junit_scan_reports_malformed_xml_as_diagnostic(tmp_path: Path) -> None:
    report = tmp_path / "broken.xml"
    report.write_text("<testsuite>")

    result = JUnitAdapter().scan(report)

    assert result.records == ()
    assert result.diagnostics[0].code == "QCOV-SCAN-001"
