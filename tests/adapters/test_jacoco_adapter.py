from pathlib import Path

from qcov.adapters.jacoco import JacocoAdapter


def test_jacoco_scan_reads_class_and_method_inventory_without_evidence(tmp_path: Path) -> None:
    report = tmp_path / "jacoco.xml"
    report.write_text(
        '<report name="demo"><package name="app"><class name="app/Refund">'
        '<method name="refund" desc="()V"/></class></package></report>'
    )

    result = JacocoAdapter().scan(report)

    assert result.adapter == "jacoco"
    assert result.records[0].identity == "app.Refund::refund()V"
    assert result.records[0].status == "unknown"
    assert not hasattr(result.records[0], "obligation")


def test_jacoco_scan_uses_class_identity_when_no_methods_are_present(tmp_path: Path) -> None:
    report = tmp_path / "jacoco.xml"
    report.write_text('<report><package name="app"><class name="app/Refund"/></package></report>')

    result = JacocoAdapter().scan(report)

    assert [record.identity for record in result.records] == ["app.Refund"]


def test_jacoco_scan_returns_diagnostic_for_invalid_xml(tmp_path: Path) -> None:
    report = tmp_path / "jacoco.xml"
    report.write_text("<report>")

    result = JacocoAdapter().scan(report)

    assert result.records == ()
    assert result.diagnostics[0].code == "QCOV-SCAN-001"
