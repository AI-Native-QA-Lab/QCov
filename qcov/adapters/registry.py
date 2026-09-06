"""Deterministic built-in inventory adapter registry."""

from qcov.adapters.base import InventoryScanner
from qcov.adapters.coverage import CoverageAdapter
from qcov.adapters.junit import JUnitAdapter
from qcov.adapters.lcov import LcovAdapter
from qcov.adapters.playwright import PlaywrightAdapter


def inventory_adapters() -> tuple[InventoryScanner, ...]:
    return (CoverageAdapter(), JUnitAdapter(), LcovAdapter(), PlaywrightAdapter())
