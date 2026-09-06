"""Read versioned QCov YAML and JSON protocol files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from .config import ProjectConfig
from .protocol import QualityEvidence, QualityPolicy, TestingObligation

Model = TypeVar("Model", bound=BaseModel)


class ProtocolLoadError(ValueError):
    """A stable error for malformed or inaccessible protocol input."""

    code = "QCOV-SCHEMA-001"


class ConfigLoadError(ValueError):
    """A stable error for malformed project configuration."""

    code = "QCOV-CONFIG-001"


def _load(path: Path, model: type[Model]) -> Model:
    try:
        raw: Any = json.loads(path.read_text()) if path.suffix == ".json" else yaml.safe_load(path.read_text())
        return model.model_validate(raw)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ValidationError) as error:
        raise ProtocolLoadError(f"{ProtocolLoadError.code}: {path}: {error}") from error


def load_obligation(path: Path) -> TestingObligation:
    return _load(path, TestingObligation)


def load_evidence(path: Path) -> QualityEvidence:
    return _load(path, QualityEvidence)


def load_policy(path: Path) -> QualityPolicy:
    return _load(path, QualityPolicy)


def load_config(path: Path) -> ProjectConfig:
    try:
        raw: Any = json.loads(path.read_text()) if path.suffix == ".json" else yaml.safe_load(path.read_text())
        return ProjectConfig.model_validate(raw)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ValidationError) as error:
        raise ConfigLoadError(f"{ConfigLoadError.code}: {path}: {error}") from error
