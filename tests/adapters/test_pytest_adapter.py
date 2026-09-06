from pathlib import Path

from qcov.adapters.pytest import PytestAdapter


def test_pytest_adapter_collects_explicit_obligation_marker(tmp_path: Path) -> None:
    (tmp_path / "test_refund.py").write_text(
        'import pytest\n\n@pytest.mark.qcov("QO-REFUND-001")\ndef test_refund():\n    pass\n'
    )

    records = PytestAdapter().collect(tmp_path)

    assert records[0].obligation.ref == "QO-REFUND-001"
    assert records[0].execution.status == "unknown"


def test_pytest_adapter_does_not_infer_unmarked_tests(tmp_path: Path) -> None:
    (tmp_path / "test_refund.py").write_text("def test_refund():\n    pass\n")

    assert PytestAdapter().collect(tmp_path) == []


def test_pytest_adapter_ignores_hidden_dependency_directories(tmp_path: Path) -> None:
    (tmp_path / "test_refund.py").write_text(
        'import pytest\n\n@pytest.mark.qcov("QO-REFUND-001")\ndef test_refund():\n    pass\n'
    )
    environment = tmp_path / ".venv"
    environment.mkdir()
    (environment / "test_dependency.py").write_text(
        'import pytest\n\n@pytest.mark.qcov("QO-DEPENDENCY-001")\ndef test_dependency():\n    pass\n'
    )

    records = PytestAdapter().collect(tmp_path)

    assert [record.obligation.ref for record in records] == ["QO-REFUND-001"]
