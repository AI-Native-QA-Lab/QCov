"""Stable renderers for PR quality coverage deltas."""

from __future__ import annotations

import json

from qcov.engine.delta import DeltaReport, ObligationDelta
from qcov.engine.reports import _as_dict
from qcov.i18n.catalog import translate


def _item(delta: ObligationDelta) -> dict[str, object]:
    return {
        "obligationId": delta.obligation_id,
        "change": delta.kind.value,
        "before": _as_dict(delta.before) if delta.before else None,
        "after": _as_dict(delta.after) if delta.after else None,
        "changedEvidenceIds": list(delta.changed_evidence_ids),
    }


def render_delta_json(report: DeltaReport) -> str:
    """Render stable, language-neutral delta JSON."""
    return json.dumps(
        {
            "baseCommit": report.base_commit,
            "headCommit": report.head_commit,
            "obligations": [_item(item) for item in report.obligations],
        },
        indent=2,
        sort_keys=True,
    )


def _dimensions(result: ObligationDelta, locale: str, side: str) -> str:
    evaluation = result.before if side == "before" else result.after
    if evaluation is None:
        return "—"
    rows = "\n".join(
        f"- {translate(f'dimension.{item.dimension.value}', locale)}: `{item.status.value}` "
        f"({', '.join(item.required_types)}); {translate('label.observed', locale)}: "
        f"{', '.join(item.observed_evidence_ids) or '—'}"
        for item in evaluation.dimensions
    )
    return f"{translate(f'delta.{side}', locale)} {translate('label.required', locale)}:\n{rows}"


def render_delta_markdown(report: DeltaReport, locale: str = "en") -> str:
    """Render an explainable localized Markdown delta summary."""
    blocks = [
        (
            f"# {translate('delta.title', locale)}\n\n"
            f"{translate('delta.base', locale)}: `{report.base_commit}`\n\n"
            f"{translate('delta.head', locale)}: `{report.head_commit}`"
        )
    ]
    for item in report.obligations:
        before = item.before.status.value if item.before else "—"
        after = item.after.status.value if item.after else "—"
        evidence = ", ".join(item.changed_evidence_ids) or "—"
        blocks.append(
            f"## {item.obligation_id}\n\n"
            f"{translate('delta.change', locale)}: `{item.kind.value}`\n\n"
            f"{translate('delta.before', locale)}: `{before}`\n\n"
            f"{translate('delta.after', locale)}: `{after}`\n\n"
            f"{translate('delta.evidence', locale)}: {evidence}\n\n"
            f"{_dimensions(item, locale, 'before')}\n\n"
            f"{_dimensions(item, locale, 'after')}"
        )
    return "\n\n".join(blocks)
