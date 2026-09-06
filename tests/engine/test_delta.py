from pathlib import Path

from qcov.engine.delta import ChangeKind, compare_snapshots
from qcov.engine.git_snapshots import Snapshot
from qcov.models.io import load_evidence, load_obligation


def _snapshot(*, evidence=(), obligation=True, commit="a") -> Snapshot:
    item = load_obligation(Path("examples/refund/obligation.yaml"))
    return Snapshot(commit, {item.metadata.id: item} if obligation else {}, {x.metadata.id: x for x in evidence})


def _evidence(name: str):
    return load_evidence(Path(f"examples/refund/evidence/{name}.yaml"))


def test_compares_added_removed_modified_and_unchanged_obligations() -> None:
    base = _snapshot(evidence=(_evidence("behavior"), _evidence("boundary"), _evidence("data")))
    changed = load_obligation(Path("examples/refund/obligation.yaml")).model_copy(
        update={"risk": {"domain": "money", "severity": "high"}}
    )
    added = changed.model_copy(update={"metadata": changed.metadata.model_copy(update={"id": "QO-NEW"})})
    head = Snapshot("b", {changed.metadata.id: changed, added.metadata.id: added}, {})

    report = compare_snapshots(base, head)

    assert [item.kind for item in report.obligations] == [ChangeKind.ADDED, ChangeKind.MODIFIED]
    changed_delta = report.obligations[1]
    assert changed_delta.before.status.value == "PARTIAL"
    assert changed_delta.after.status.value == "UNKNOWN"
    assert changed_delta.changed_evidence_ids == ("QE-REFUND-BEHAVIOR-001", "QE-REFUND-BOUNDARY-001", "QE-REFUND-DATA-001")


def test_marks_same_definition_and_referenced_evidence_as_unchanged() -> None:
    evidence = (_evidence("behavior"),)
    report = compare_snapshots(_snapshot(evidence=evidence), _snapshot(evidence=evidence, commit="b"))
    assert report.obligations[0].kind is ChangeKind.UNCHANGED


def test_ignores_unreferenced_evidence_for_obligation_delta() -> None:
    original = _evidence("behavior")
    unrelated = original.model_copy(
        update={
            "metadata": original.metadata.model_copy(update={"id": "QE-OTHER"}),
            "obligation": original.obligation.model_copy(update={"ref": "QO-OTHER"}),
        }
    )
    report = compare_snapshots(_snapshot(), _snapshot(evidence=(unrelated,), commit="b"))
    assert report.obligations[0].kind is ChangeKind.UNCHANGED


def test_reports_removed_obligation() -> None:
    report = compare_snapshots(_snapshot(), _snapshot(obligation=False, commit="b"))
    assert report.obligations[0].kind is ChangeKind.REMOVED
    assert report.obligations[0].after is None
