"""Proposal request contexts (inputs only; never QualityEvidence)."""

from __future__ import annotations

from dataclasses import dataclass

from qcov.models.protocol import TestingObligation


@dataclass(frozen=True)
class ObligationSuggestContext:
    requirements_text: str
    requirements_refs: tuple[str, ...]
    obligations: tuple[TestingObligation, ...]


@dataclass(frozen=True)
class ChangeRiskContext:
    diff_text: str
    base_ref: str
    head_ref: str
    obligations: tuple[TestingObligation, ...]
