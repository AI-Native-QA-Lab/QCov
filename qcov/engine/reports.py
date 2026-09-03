"""Human-readable and machine-readable evaluation reports."""

from __future__ import annotations

import json
from collections.abc import Sequence

from qcov.engine.gaps import ObligationResult
from qcov.i18n.catalog import translate


def _as_dict(result: ObligationResult) -> dict[str, object]:
    return {
        "obligationId": result.obligation_id,
        "status": result.status.value,
        "dimensions": [
            {
                "dimension": item.dimension.value,
                "requiredTypes": list(item.required_types),
                "status": item.status.value,
                "observedEvidenceIds": list(item.observed_evidence_ids),
            }
            for item in result.dimensions
        ],
    }


def render_json(results: Sequence[ObligationResult]) -> str:
    """Return stable, language-neutral JSON output."""
    return json.dumps({"results": [_as_dict(result) for result in results]}, indent=2, sort_keys=True)


def render_markdown(results: Sequence[ObligationResult], locale: str = "en") -> str:
    """Render an explainable localized Markdown summary."""
    blocks: list[str] = []
    for result in results:
        dimensions = "\n".join(
            f"- {translate(f'dimension.{item.dimension.value}', locale)}: `{item.status.value}` "
            f"({', '.join(item.required_types)})"
            for item in result.dimensions
        )
        unproven = ", ".join(
            translate(f"dimension.{item.dimension.value}", locale)
            for item in result.unproven_dimensions
        ) or "—"
        blocks.append(
            f"## {result.obligation_id}\n\n"
            f"{translate('label.status', locale)}: `{result.status.value}`\n\n"
            f"{translate('label.required', locale)}:\n{dimensions}\n\n"
            f"{translate('label.unproven', locale)}: {unproven}"
        )
    return "\n\n".join(blocks)
