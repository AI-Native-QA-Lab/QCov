"""AST-only collection of explicit pytest QCov markers."""

from __future__ import annotations

import ast
from pathlib import Path

from qcov.adapters.base import DetectionResult
from qcov.models.protocol import QualityEvidence


class PytestAdapter:
    """Collect literal ``@pytest.mark.qcov("QO-...")`` mappings safely."""

    name = "pytest-marker"

    def detect(self, project_path: Path) -> DetectionResult:
        found = bool(self.test_files(project_path))
        return DetectionResult(self.name, found, "Python test files found" if found else "No Python test files")

    def test_files(self, project_path: Path) -> tuple[Path, ...]:
        """Return project test files while excluding hidden dependency trees."""
        return tuple(
            path
            for path in sorted(project_path.rglob("test_*.py"))
            if not any(part.startswith(".") for part in path.relative_to(project_path).parts)
        )

    def collect(self, project_path: Path) -> list[QualityEvidence]:
        records: list[QualityEvidence] = []
        for path in self.test_files(project_path):
            records.extend(self._collect_file(path, project_path))
        return records

    def _collect_file(self, path: Path, root: Path) -> list[QualityEvidence]:
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
        except (OSError, SyntaxError):
            return []
        records: list[QualityEvidence] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    ref = _obligation_ref(decorator)
                    if ref is not None:
                        records.append(_unknown_evidence(ref, path.relative_to(root).as_posix(), node.name))
        return records


def _obligation_ref(decorator: ast.expr) -> str | None:
    if not isinstance(decorator, ast.Call) or len(decorator.args) != 1:
        return None
    if not isinstance(decorator.args[0], ast.Constant) or not isinstance(decorator.args[0].value, str):
        return None
    target = decorator.func
    if not (
        isinstance(target, ast.Attribute)
        and target.attr == "qcov"
        and isinstance(target.value, ast.Attribute)
        and target.value.attr == "mark"
        and isinstance(target.value.value, ast.Name)
        and target.value.value.id == "pytest"
    ):
        return None
    return decorator.args[0].value


def _unknown_evidence(obligation_ref: str, path: str, test_name: str) -> QualityEvidence:
    return QualityEvidence.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityEvidence",
            "metadata": {"id": f"QE-PYTEST-{obligation_ref}-{test_name}"},
            "obligation": {"ref": obligation_ref},
            "evidence": {"dimension": "behavior", "type": "pytest_marker"},
            "producer": {"name": "pytest", "adapter": "qcov-pytest"},
            "execution": {"status": "unknown", "timestamp": "1970-01-01T00:00:00+00:00"},
            "artifact": {"path": path},
            "confidence": {"deterministic": True, "reproducible": True},
        }
    )
