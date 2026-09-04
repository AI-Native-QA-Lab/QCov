"""Built-in producers that normalize external signals into Quality Evidence."""

from .junit import JUnitAdapter
from .pytest import PytestAdapter

__all__ = ["JUnitAdapter", "PytestAdapter"]
