"""Stable, typed error codes for QCov model and proposal loading."""

from __future__ import annotations


class ProposalInputError(ValueError):
    """Stable errors for proposal inputs, loading, and provider resolution."""


class AgentInputError(ValueError):
    """Stable errors for agent CLI inputs and targets."""

    CODE_NOT_QUALITY_PLAN = "QCOV-AGENT-001"
    CODE_TARGET_NOT_FOUND = "QCOV-AGENT-002"

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
