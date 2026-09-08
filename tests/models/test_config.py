from __future__ import annotations

from pathlib import Path

import pytest

from qcov.models.config import ProjectConfig, resolve_paths
from qcov.models.io import ConfigLoadError, load_config


def write_config(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "qcov.yaml"
    path.write_text(
        "apiVersion: qcov.dev/v1alpha1\n"
        "kind: QCovConfig\n"
        "obligations: [obligations/*.yaml]\n"
        f"{content}\n"
    )
    return path


def test_config_resolves_relative_globs_in_sorted_order(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "b.yaml").write_text("example")
    (reports / "a.yaml").write_text("example")
    config_path = write_config(tmp_path, "evidence: [reports/*.yaml]")

    paths = resolve_paths(load_config(config_path), config_path)

    assert [path.name for path in paths.evidence] == ["a.yaml", "b.yaml"]


def test_invalid_config_uses_stable_error_code(tmp_path: Path) -> None:
    config_path = tmp_path / "qcov.yaml"
    config_path.write_text("kind: QCovConfig\n")

    with pytest.raises(ConfigLoadError, match="QCOV-CONFIG-001"):
        load_config(config_path)


def test_config_requires_qcov_config_kind() -> None:
    with pytest.raises(ValueError):
        ProjectConfig.model_validate({"apiVersion": "qcov.dev/v1alpha1", "kind": "wrong"})


def test_config_resolves_playwright_and_lcov_scan_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "qcov.yaml"
    config_path.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        "scan:\n  playwright: [reports/playwright.json]\n  lcov: [reports/lcov.info]\n"
    )
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports/playwright.json").write_text("{}")
    (tmp_path / "reports/lcov.info").write_text("")

    paths = resolve_paths(load_config(config_path), config_path)

    assert paths.playwright == ((tmp_path / "reports/playwright.json").resolve(),)
    assert paths.lcov == ((tmp_path / "reports/lcov.info").resolve(),)


def test_config_resolves_mapping_paths(tmp_path: Path) -> None:
    mapping = tmp_path / "mappings"
    mapping.mkdir()
    (mapping / "a.yaml").write_text("x")
    config_path = tmp_path / "qcov.yaml"
    config_path.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
        "mapping: [mappings/*.yaml]\n"
    )
    paths = resolve_paths(load_config(config_path), config_path)
    assert paths.mapping == ((mapping / "a.yaml").resolve(),)
