"""Run proposal providers with input checks and stable error mapping."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qcov.ai.context import ChangeRiskContext, ObligationSuggestContext
from qcov.models.errors import ProposalInputError
from qcov.models.protocol import QualityProposal

if TYPE_CHECKING:
    from qcov.ai.provider import AIProvider


def propose_obligations(
    context: ObligationSuggestContext, provider: AIProvider
) -> QualityProposal:
    if not context.requirements_text.strip():
        raise ProposalInputError("QCOV-PROPOSAL-002: requirements input is required")
    try:
        return provider.propose_obligations(context)
    except ProposalInputError:
        raise
    except Exception as error:
        raise ProposalInputError(f"QCOV-AI-002: provider call failed: {error}") from error


def analyze_change(context: ChangeRiskContext, provider: AIProvider) -> QualityProposal:
    if not context.diff_text.strip():
        raise ProposalInputError("QCOV-PROPOSAL-002: local diff input is required")
    try:
        return provider.analyze_change(context)
    except ProposalInputError:
        raise
    except Exception as error:
        raise ProposalInputError(f"QCOV-AI-002: provider call failed: {error}") from error
