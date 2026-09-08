"""AI package for proposal-only providers."""

from qcov.ai.context import ChangeRiskContext, ObligationSuggestContext
from qcov.ai.propose import analyze_change, propose_obligations
from qcov.ai.provider import AIProvider, OfflineProvider, resolve_provider

__all__ = [
    "AIProvider",
    "ChangeRiskContext",
    "ObligationSuggestContext",
    "OfflineProvider",
    "analyze_change",
    "propose_obligations",
    "resolve_provider",
]
