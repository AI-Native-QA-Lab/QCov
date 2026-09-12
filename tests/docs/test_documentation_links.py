import json
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
        "production-evidence.md",
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


def test_readmes_link_to_production_evidence_guides() -> None:
    assert "docs/en/production-evidence.md" in (ROOT / "README.md").read_text()
    assert "docs/zh-CN/production-evidence.md" in (ROOT / "README.zh-CN.md").read_text()


def test_roadmaps_start_qcov_1_0_after_delivered_iteration_8() -> None:
    for path, delivered_heading in (
        (ROOT / "docs/en/roadmap.md", "Delivered through Iteration 8"),
        (ROOT / "docs/zh-CN/roadmap.md", "已交付至 Iteration 8"),
    ):
        text = path.read_text()
        assert delivered_heading in text
        assert "Iteration 9" in text
        assert "QCov 1.0" in text
        assert "Documentation and onboarding" in text
        assert "Roadmap Complete through Iteration 8" not in text


def test_protocol_docs_link_to_impact_schema() -> None:
    schema = ROOT / "schemas" / "qcov.impact-v1.schema.json"
    assert schema.exists()
    payload = json.loads(schema.read_text())
    assert payload["properties"]["contractVersion"]["const"] == "qcov.impact/v1"
    assert set(payload["required"]) >= {
        "contractVersion",
        "changedFiles",
        "affectedObligations",
        "newGaps",
        "resolvedGaps",
        "diagnostics",
    }
    for path in (ROOT / "docs/en/protocol.md", ROOT / "docs/zh-CN/protocol.md"):
        assert "../../schemas/qcov.impact-v1.schema.json" in path.read_text()
