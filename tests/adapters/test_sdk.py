from pathlib import Path

from qcov.adapters import sdk
from qcov.adapters.junit import JUnitAdapter
from qcov.adapters.sdk import ADAPTER_PROTOCOL_VERSION, InventoryAdapter, ScanDiagnostic


def test_inventory_adapter_protocol_exposes_versioned_scan_contract(tmp_path: Path) -> None:
    adapter = JUnitAdapter()

    assert adapter.name == "junit"
    assert adapter.protocol_version == ADAPTER_PROTOCOL_VERSION == "qcov.adapter/v1"
    assert isinstance(adapter, InventoryAdapter)
    assert adapter.scan(tmp_path / "missing.xml").adapter == "junit"


def test_sdk_reexports_scan_diagnostic() -> None:
    assert ScanDiagnostic.__module__ == "qcov.adapters.base"


def test_sdk_wildcard_surface_contains_all_contract_types() -> None:
    assert set(sdk.__all__) == {
        "ADAPTER_PROTOCOL_VERSION",
        "InventoryAdapter",
        "ScanDiagnostic",
        "ScanResult",
    }
