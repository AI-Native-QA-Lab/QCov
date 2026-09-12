from pathlib import Path

import yaml

from qcov.models.io import load_config, load_obligation

ROOT = Path(__file__).parents[2]
CASE_STUDIES = ROOT / "examples/case-studies"


def test_case_studies_are_reproducible_and_honest_release_gate_inputs() -> None:
    expected = {
        "ai-native-qa-agents": "Python pytest coverage",
        "ai4se-demo-project": "Java JUnit JaCoCo",
        "naodeng.com.cn": "TypeScript Playwright",
    }

    for case_id, stack in expected.items():
        case_root = CASE_STUDIES / case_id
        metadata = yaml.safe_load((case_root / "metadata.yaml").read_text())
        assert metadata["case_id"] == case_id
        assert metadata["stack"] == stack
        assert len(metadata["source"]["commit"]) == 40
        assert metadata["source"]["repository"]
        assert metadata["source"]["redaction"]
        assert metadata["commands"]
        assert metadata["obligation_status"] in {
                "SOURCE_DERIVED_PENDING_OWNER_REVIEW",
                "SOURCE_DERIVED_REVIEWED_PENDING_OWNER_ACCEPTANCE",
                "OWNER_ACCEPTED",
        }
        if metadata["obligation_status"] == "SOURCE_DERIVED_REVIEWED_PENDING_OWNER_ACCEPTANCE":
            review = metadata["obligation_review"]
            assert review["reviewer"]
            assert review["reviewed_at"]
            assert review["result"]
        assert metadata["execution_status"] in {"PASSED", "BLOCKED", "NOT_RUN"}
        if metadata["execution_status"] != "NOT_RUN":
            assert metadata["verification"]["environment"]
            assert metadata["verification"]["command"]
            assert metadata["verification"]["result"]
        assert metadata["release_gate_status"] == "NOT_MET"

        obligations = sorted((case_root / "obligations").glob("*.yaml"))
        assert len(obligations) >= 10
        for obligation_path in obligations:
            obligation = load_obligation(obligation_path)
            assert obligation.source.ref
            assert obligation.source.ref in metadata["source"]["reference_files"]

        config = load_config(case_root / "qcov.yaml")
        assert config.obligations == ["obligations/*.yaml"]
        assert config.evidence == []
        assert config.mapping == ["mapping.yaml"]

    assert (ROOT / "docs/case-studies/README.md").is_file()
    assert (ROOT / "docs/case-studies/README.zh-CN.md").is_file()
