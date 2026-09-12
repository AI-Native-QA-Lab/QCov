"""Deterministic built-in inventory adapter registry."""

from qcov.adapters.coverage import CoverageAdapter
from qcov.adapters.jacoco import JacocoAdapter
from qcov.adapters.junit import JUnitAdapter
from qcov.adapters.lcov import LcovAdapter
from qcov.adapters.playwright import PlaywrightAdapter
from qcov.adapters.production_observation import ProductionObservationAdapter
from qcov.adapters.sdk import InventoryAdapter


def inventory_adapters() -> tuple[InventoryAdapter, ...]:
    return (
        CoverageAdapter(),
        JUnitAdapter(),
        JacocoAdapter(),
        LcovAdapter(),
        PlaywrightAdapter(),
        ProductionObservationAdapter(),
    )
