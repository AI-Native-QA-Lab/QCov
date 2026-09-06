from qcov.adapters.registry import inventory_adapters


def test_inventory_registry_has_stable_adapter_names() -> None:
    assert [adapter.name for adapter in inventory_adapters()] == [
        "coverage.py", "junit", "lcov", "playwright"
    ]
