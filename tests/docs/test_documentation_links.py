from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_readmes_link_to_each_other() -> None:
    assert "README.zh-CN.md" in (ROOT / "README.md").read_text()
    assert "README.md" in (ROOT / "README.zh-CN.md").read_text()


def test_bilingual_docs_have_matching_stems() -> None:
    english = {path.name for path in (ROOT / "docs/en").glob("*.md")}
    chinese = {path.name for path in (ROOT / "docs/zh-CN").glob("*.md")}
    expected = {
        "agent.md",
        "architecture.md",
        "concepts.md",
        "development.md",
        "getting-started.md",
        "mapping.md",
        "process.md",
            "policy.md",
            "pr-delta.md",
            "production-evidence.md",
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


def test_roadmaps_define_the_1_0_to_2_0_evolution() -> None:
    english = (ROOT / "docs/en/roadmap.md").read_text()
    chinese = (ROOT / "docs/zh-CN/roadmap.md").read_text()

    for text in (english, chinese):
        assert "Iteration 9" in text
        assert "QCov 1.0" in text
        assert "QCov 1.5" in text
        assert "QCov 2.0" in text
        assert "Roadmap Complete through Iteration 8" not in text


def test_bilingual_onboarding_documents_the_supported_five_minute_flow() -> None:
    documents = (
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "docs/en/getting-started.md",
        ROOT / "docs/zh-CN/getting-started.md",
    )
    required = (
        "qcov gaps",
        "qcov scan",
        "qcov map preview",
        "qcov policy check",
        "qcov diff",
        "Python",
        "Java",
        "TypeScript",
        "coverage.py",
        "LCOV",
    )

    for path in documents:
        text = path.read_text()
        for value in required:
            assert value in text, f"{path} must document {value}"

    for path in documents[2:]:
        text = path.read_text()
        assert "qcov impact" in text
        assert "qcov affected" in text
        assert "implemented change-impact command" in text or "已实现的变更影响命令" in text


def test_readmes_link_to_production_evidence_guides() -> None:
    assert "docs/en/production-evidence.md" in (ROOT / "README.md").read_text()
    assert "docs/zh-CN/production-evidence.md" in (ROOT / "README.zh-CN.md").read_text()
