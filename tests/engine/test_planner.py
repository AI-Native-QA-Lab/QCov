from __future__ import annotations

from qcov.engine.gaps import DimensionResult, ObligationResult, evaluate_obligation
from qcov.engine.planner import build_quality_plan
from qcov.models.protocol import CoverageStatus, QualityDimension, TestingObligation


def _obligation(**overrides: object) -> TestingObligation:
    base = {
        "apiVersion": "qcov.dev/v1alpha1",
        "kind": "TestingObligation",
        "metadata": {
            "id": "QO-A",
            "title": {"en": "A", "zh-CN": "甲"},
        },
        "source": {"type": "requirement", "ref": "A"},
        "risk": {"domain": "x", "severity": "critical"},
        "requiredEvidence": {"behavior": ["api_test"], "security": ["e2e_test"]},
    }
    base.update(overrides)
    return TestingObligation.model_validate(base)


def test_planner_orders_by_priority_score() -> None:
    obl = _obligation()
    # no evidence → Gap Engine marks dimensions UNKNOWN (not MISSING)
    result = evaluate_obligation(obl, [])
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.proposal.type == "quality_plan"
    assert proposal.source.kind == "evaluation_gaps"
    assert proposal.provider.name == "offline"
    ranks = [item.detail["rank"] for item in proposal.items]
    assert ranks == [1, 2]
    # security: benefit 20+40+25=85, cost 35 → priority -50
    # behavior: benefit 20+40+10=70, cost 10 → priority -60  → behavior first
    assert proposal.items[0].obligation_ref == "QO-A"
    assert proposal.items[0].detail["dimension"] == "behavior"
    assert proposal.items[0].detail["gapStatus"] == "UNKNOWN"
    assert proposal.items[0].detail["suggestedEvidenceType"] == "api_test"
    assert proposal.items[0].detail["priorityScore"] == -60
    assert proposal.items[1].detail["dimension"] == "security"
    assert proposal.items[1].detail["priorityScore"] == -50


def test_planner_missing_status_scores_higher_than_unknown() -> None:
    """Hand-build results: MISSING outranks UNKNOWN when other factors equal."""
    obl = _obligation(
        requiredEvidence={"behavior": ["api_test"]},
        risk={"domain": "x", "severity": "low"},
    )
    missing = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                ("api_test",),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    proposal = build_quality_plan([missing], [obl], refs=["fixture"])
    assert proposal.items[0].detail["gapStatus"] == "MISSING"
    assert proposal.items[0].detail["benefitScore"] == 50 + 10 + 10  # missing+low+behavior
    assert proposal.items[0].detail["priorityScore"] == 10 - 70


def test_planner_empty_required_types_uses_default_cost() -> None:
    obl = _obligation(requiredEvidence={"behavior": []})
    result = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                (),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.items[0].detail["costScore"] == 40
    assert proposal.items[0].detail["suggestedEvidenceType"] is None
    assert proposal.items[0].detail["missingEvidenceTypes"] == []


def test_planner_empty_when_all_covered() -> None:
    from qcov.models.protocol import QualityEvidence

    obl = _obligation(
        requiredEvidence={"behavior": ["api_test"]},
    )
    evidence = QualityEvidence.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityEvidence",
            "metadata": {"id": "QE-1"},
            "obligation": {"ref": "QO-A"},
            "evidence": {"dimension": "behavior", "type": "api_test"},
            "producer": {"name": "pytest"},
            "execution": {
                "status": "passed",
                "timestamp": "2026-09-08T12:00:00+08:00",
            },
            "artifact": {"path": "t"},
            "confidence": {"deterministic": True, "reproducible": True},
        }
    )
    result = evaluate_obligation(obl, [evidence])
    assert result.status is CoverageStatus.COVERED
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.items == []


def test_planner_picks_cheapest_suggested_type() -> None:
    obl = _obligation(
        requiredEvidence={"behavior": ["e2e_test", "api_test"]},
    )
    result = evaluate_obligation(obl, [])
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.items[0].detail["suggestedEvidenceType"] == "api_test"
    assert proposal.items[0].detail["costScore"] == 10
    assert proposal.items[0].detail["missingEvidenceTypes"] == ["api_test", "e2e_test"]


def test_planner_is_deterministic() -> None:
    obl = _obligation()
    result = evaluate_obligation(obl, [])
    a = build_quality_plan([result], [obl], refs=["r"])
    b = build_quality_plan([result], [obl], refs=["r"])
    assert a.model_dump(by_alias=True, mode="json") == b.model_dump(by_alias=True, mode="json")


def test_planner_tie_break_by_obligation_id() -> None:
    """Equal priorityScore: lower obligation_id ranks first."""
    low = {"domain": "x", "severity": "low"}
    obl_a = _obligation(
        metadata={"id": "QO-A", "title": {"en": "A", "zh-CN": "甲"}},
        requiredEvidence={"behavior": ["api_test"]},
        risk=low,
    )
    obl_b = _obligation(
        metadata={"id": "QO-B", "title": {"en": "B", "zh-CN": "乙"}},
        requiredEvidence={"behavior": ["api_test"]},
        risk=low,
        source={"type": "requirement", "ref": "B"},
    )
    missing_a = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                ("api_test",),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    missing_b = ObligationResult(
        "QO-B",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                ("api_test",),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    proposal = build_quality_plan(
        [missing_b, missing_a], [obl_a, obl_b], refs=["fixture"]
    )
    assert len(proposal.items) == 2
    assert proposal.items[0].detail["priorityScore"] == -60
    assert proposal.items[1].detail["priorityScore"] == -60
    assert proposal.items[0].obligation_ref == "QO-A"
    assert proposal.items[1].obligation_ref == "QO-B"
    assert proposal.items[0].detail["rank"] == 1
    assert proposal.items[1].detail["rank"] == 2


def test_planner_tie_break_by_dimension() -> None:
    """Equal priorityScore and obligation_id: dimension value breaks tie."""
    obl = _obligation(
        requiredEvidence={"boundary": ["api_test"], "integration": ["api_test"]},
        risk={"domain": "x", "severity": "low"},
    )
    result = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.INTEGRATION,
                ("api_test",),
                CoverageStatus.MISSING,
                (),
            ),
            DimensionResult(
                QualityDimension.BOUNDARY,
                ("api_test",),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.items[0].detail["priorityScore"] == -65
    assert proposal.items[1].detail["priorityScore"] == -65
    assert proposal.items[0].detail["dimension"] == "boundary"
    assert proposal.items[1].detail["dimension"] == "integration"


def test_planner_tie_break_by_first_missing_evidence_type() -> None:
    """Equal priorityScore, obligation_id, and dimension: missing type breaks tie."""
    obl = _obligation(
        requiredEvidence={"behavior": ["api_test"]},
        risk={"domain": "x", "severity": "low"},
    )
    junit_row = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                ("junit_test",),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    api_row = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                ("api_test",),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    proposal = build_quality_plan([junit_row, api_row], [obl], refs=["fixture"])
    assert len(proposal.items) == 2
    assert proposal.items[0].detail["missingEvidenceTypes"] == ["api_test"]
    assert proposal.items[1].detail["missingEvidenceTypes"] == ["junit_test"]
    assert proposal.items[0].detail["rank"] == 1
    assert proposal.items[1].detail["rank"] == 2
