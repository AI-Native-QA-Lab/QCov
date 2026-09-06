from pathlib import Path

from qcov.adapters.lcov import LcovAdapter


def test_lcov_scan_aggregates_line_counts_per_source(tmp_path: Path) -> None:
    path = tmp_path / "lcov.info"
    path.write_text(
        "TN:\nSF:src/a.ts\nDA:1,2\nDA:2,0,checksum\nLF:2\nLH:1\nend_of_record\n"
        "SF:src/b.ts\nDA:4,3\nend_of_record\n"
    )

    result = LcovAdapter().scan(path)

    assert [(record.identity, record.metadata) for record in result.records] == [
        ("src/a.ts", {"instrumentedLines": "2", "hitLines": "1"}),
        ("src/b.ts", {"instrumentedLines": "1", "hitLines": "1"}),
    ]


def test_lcov_scan_reports_invalid_section(tmp_path: Path) -> None:
    path = tmp_path / "lcov.info"
    path.write_text("DA:1,1\n")

    result = LcovAdapter().scan(path)

    assert result.records == ()
    assert result.diagnostics[0].code == "QCOV-SCAN-001"


def test_lcov_scan_reports_unterminated_source_section(tmp_path: Path) -> None:
    path = tmp_path / "lcov.info"
    path.write_text("SF:src/a.ts\nDA:1,1\n")

    result = LcovAdapter().scan(path)

    assert result.records == ()
    assert result.diagnostics[0].code == "QCOV-SCAN-001"
