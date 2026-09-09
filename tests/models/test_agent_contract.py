from __future__ import annotations

import pytest
from pydantic import ValidationError

from qcov.models.agent_contract import AgentEnvelope
from qcov.models.errors import AgentInputError


def test_agent_envelope_accepts_explain_payload() -> None:
    envelope = AgentEnvelope.model_validate(
        {
            "contractVersion": "qcov.agent/v1",
            "command": "explain",
            "payload": {
                "mode": "gap",
                "obligationId": "QO-REFUND-001",
                "dimension": "behavior",
                "status": "MISSING",
                "requiredTypes": ["api_test"],
                "observedEvidenceIds": [],
                "reasons": [
                    {
                        "code": "NO_EVIDENCE_FOR_OBLIGATION",
                        "summary": {
                            "en": "No evidence references this obligation.",
                            "zh-CN": "没有指向该义务的证据。",
                        },
                    }
                ],
            },
        }
    )
    assert envelope.contract_version == "qcov.agent/v1"
    assert envelope.command == "explain"
    assert envelope.payload.mode == "gap"


def test_agent_envelope_rejects_unknown_contract_version() -> None:
    with pytest.raises(ValidationError):
        AgentEnvelope.model_validate(
            {
                "contractVersion": "qcov.agent/v0",
                "command": "explain",
                "payload": {
                    "mode": "gap",
                    "obligationId": "QO-1",
                    "dimension": "behavior",
                    "status": "MISSING",
                    "requiredTypes": [],
                    "observedEvidenceIds": [],
                    "reasons": [],
                },
            }
        )


def test_agent_input_error_codes() -> None:
    assert AgentInputError.CODE_NOT_QUALITY_PLAN == "QCOV-AGENT-001"
    assert AgentInputError.CODE_TARGET_NOT_FOUND == "QCOV-AGENT-002"
