from __future__ import annotations

from qcov.engine.gaps import DimensionResult, ObligationResult
from qcov.engine.reports import render_json, render_markdown
from qcov.models.protocol import CoverageStatus, QualityDimension


def partial_refund_result() -> ObligationResult:
    return ObligationResult(
        obligation_id="QO-REFUND-001",
        status=CoverageStatus.PARTIAL,
        dimensions=(
            DimensionResult(QualityDimension.BEHAVIOR, ("api_test",), CoverageStatus.COVERED, ("QE-1",)),
            DimensionResult(QualityDimension.CONCURRENCY, ("concurrency_test",), CoverageStatus.MISSING, ()),
        ),
    )


def test_markdown_names_missing_concurrency_in_chinese() -> None:
    report = render_markdown([partial_refund_result()], locale="zh-CN")
    assert "并发" in report
    assert "PARTIAL" in report


def test_markdown_lists_observed_evidence_ids() -> None:
    report = render_markdown([partial_refund_result()])

    assert "Observed evidence" in report
    assert "QE-1" in report


def test_json_preserves_english_protocol_keys() -> None:
    assert '"obligationId"' in render_json([partial_refund_result()])
