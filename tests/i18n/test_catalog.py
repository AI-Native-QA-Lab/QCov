from qcov.i18n.catalog import translate


def test_catalog_translates_dimension_to_chinese() -> None:
    assert translate("dimension.concurrency", "zh-CN") == "并发"
