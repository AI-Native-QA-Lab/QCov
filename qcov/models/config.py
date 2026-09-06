"""QCov project configuration and deterministic local-path resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import Field

from .protocol import ProtocolModel


class ScanConfig(ProtocolModel):
    """Optional report paths grouped by supported local producer."""

    junit: list[str] = Field(default_factory=list)
    coverage: list[str] = Field(default_factory=list)


class ProjectConfig(ProtocolModel):
    """Strict, versioned configuration for one local QCov project."""

    api_version: Literal["qcov.dev/v1alpha1"] = Field(alias="apiVersion")
    kind: Literal["QCovConfig"]
    obligations: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    scan: ScanConfig = Field(default_factory=ScanConfig)


@dataclass(frozen=True)
class ResolvedPaths:
    """Sorted, deduplicated configuration paths relative to the config file."""

    obligations: tuple[Path, ...]
    evidence: tuple[Path, ...]
    junit: tuple[Path, ...]
    coverage: tuple[Path, ...]


def resolve_patterns(
    patterns: list[str], base: Path, *, include_missing: bool = False
) -> tuple[Path, ...]:
    """Resolve sorted, deduplicated paths, optionally retaining absent inputs."""
    paths: dict[Path, None] = {}
    for pattern in patterns:
        candidate = Path(pattern)
        if candidate.is_absolute():
            matches = sorted(candidate.parent.glob(candidate.name))
        else:
            matches = sorted(base.glob(pattern))
        for path in matches:
            paths[path.resolve()] = None
        if include_missing and not matches:
            paths[(candidate if candidate.is_absolute() else base / candidate).resolve()] = None
    return tuple(sorted(paths))


def resolve_paths(config: ProjectConfig, config_path: Path) -> ResolvedPaths:
    """Resolve config patterns relative to the configuration file location."""
    base = config_path.resolve().parent
    return ResolvedPaths(
        obligations=resolve_patterns(config.obligations, base),
        evidence=resolve_patterns(config.evidence, base),
        junit=resolve_patterns(config.scan.junit, base),
        coverage=resolve_patterns(config.scan.coverage, base),
    )
