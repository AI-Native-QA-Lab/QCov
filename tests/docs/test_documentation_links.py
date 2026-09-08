from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_readmes_link_to_each_other() -> None:
    assert "README.zh-CN.md" in (ROOT / "README.md").read_text()
    assert "README.md" in (ROOT / "README.zh-CN.md").read_text()


def test_bilingual_docs_have_matching_stems() -> None:
    english = {path.name for path in (ROOT / "docs/en").glob("*.md")}
    chinese = {path.name for path in (ROOT / "docs/zh-CN").glob("*.md")}
    expected = {
        "architecture.md",
        "concepts.md",
        "development.md",
        "mapping.md",
        "process.md",
        "policy.md",
        "pr-delta.md",
        "protocol.md",
        "requirements.md",
        "roadmap.md",
        "technical-design.md",
    }
    assert english == chinese == expected


def test_readmes_document_config_driven_scan() -> None:
    assert "qcov scan --config" in (ROOT / "README.md").read_text()
    assert "qcov scan --config" in (ROOT / "README.zh-CN.md").read_text()


def test_docs_name_iteration_two_inventory_adapters() -> None:
    for path in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
        text = path.read_text()
        assert "scan.playwright" in text
        assert "scan.lcov" in text
