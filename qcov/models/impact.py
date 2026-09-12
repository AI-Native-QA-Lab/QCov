"""Strict configuration models for deterministic local change impact."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .protocol import ProtocolModel


class ImpactMapping(ProtocolModel):
    """Explicit repository path glob to Testing Obligation mapping."""

    id: str = Field(min_length=1)
    paths: list[str] = Field(min_length=1)
    obligations: list[str] = Field(min_length=1)


class QualityImpactConfig(ProtocolModel):
    """Versioned, local-only configuration for Change to Obligation Impact."""

    api_version: Literal["qcov.dev/v1alpha1"] = Field(alias="apiVersion")
    kind: Literal["QualityImpactConfig"]
    mappings: list[ImpactMapping] = Field(min_length=1)
