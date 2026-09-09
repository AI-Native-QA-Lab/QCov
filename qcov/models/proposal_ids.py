"""Stable identifiers for draft QualityProposal envelopes."""

from __future__ import annotations

import hashlib

OFFLINE_CREATED_AT = "1970-01-01T00:00:00+00:00"


def stable_proposal_id(proposal_type: str, refs: list[str], item_ids: list[str]) -> str:
    digest = hashlib.sha256(
        "\0".join([proposal_type, *refs, *item_ids]).encode("utf-8")
    ).hexdigest()[:12]
    return f"QP-{digest}"
