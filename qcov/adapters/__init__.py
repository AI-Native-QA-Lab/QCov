"""Built-in producers that normalize external signals into Quality Evidence."""

from .coverage import CoverageAdapter
from .junit import JUnitAdapter
from .pytest import PytestAdapter

__all__ = ["CoverageAdapter", "JUnitAdapter", "PytestAdapter"]
