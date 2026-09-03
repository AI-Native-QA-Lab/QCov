"""Stable QCov engine error identifiers."""


class QCovEngineError(ValueError):
    """Base engine error with a stable public code."""

    code = "QCOV-ENGINE-001"
