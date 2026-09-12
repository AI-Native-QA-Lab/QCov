"""Stable renderers for qcov.impact/v1 reports."""

from __future__ import annotations

import json

from qcov.engine.impact import AffectedReport, ImpactDiagnostic, ImpactReport


def _diagnostic(diagnostic: ImpactDiagnostic) -> dict[str, object]:
    payload: dict[str, object] = {
        "code": diagnostic.code,
        "message": diagnostic.message,
        "severity": diagnostic.severity,
    }
    if diagnostic.path is not None:
        payload["path"] = diagnostic.path
    return payload


def impact_payload(report: ImpactReport) -> dict[str, object]:
    """Return the stable language-neutral qcov.impact/v1 payload."""
    return {
        "contractVersion": "qcov.impact/v1",
        "changedFiles": list(report.changed_files),
        "affectedObligations": list(report.affected_obligations),
        "newGaps": [item.as_dict() for item in report.new_gaps],
        "resolvedGaps": [item.as_dict() for item in report.resolved_gaps],
        "diagnostics": [_diagnostic(item) for item in report.diagnostics],
    }


def render_impact_json(report: ImpactReport) -> str:
    return json.dumps(impact_payload(report), indent=2, sort_keys=True)


def render_impact_markdown(report: ImpactReport) -> str:
    lines = ["# Change to Obligation Impact", "", "## Changed files", ""]
    lines.extend(f"- `{item}`" for item in report.changed_files)
    lines.extend(["", "## Affected obligations", ""])
    lines.extend(f"- `{item}`" for item in report.affected_obligations)
    lines.extend(["", "## Diagnostics", ""])
    lines.extend(
        f"- `{item.code}` ({item.severity}): {item.message}"
        + (f" — `{item.path}`" if item.path else "")
        for item in report.diagnostics
    )
    return "\n".join(lines)


def render_affected_json(report: AffectedReport) -> str:
    """Render stable current-state output without delta semantics."""
    return json.dumps(
        {
            "contractVersion": "qcov.impact/v1",
            "changedFiles": list(report.changed_files),
            "affectedObligations": list(report.affected_obligations),
            "newGaps": [],
            "resolvedGaps": [],
            "diagnostics": [_diagnostic(item) for item in report.diagnostics],
            "keyGaps": [item.as_dict() for item in report.key_gaps],
        },
        indent=2,
        sort_keys=True,
    )


def render_affected_markdown(report: AffectedReport) -> str:
    """Render a concise current-state affected-obligation summary."""
    lines = ["# Affected quality gaps", "", "## Changed files", ""]
    lines.extend(f"- `{item}`" for item in report.changed_files)
    lines.extend(["", "## Affected obligations", ""])
    lines.extend(f"- `{item}`" for item in report.affected_obligations)
    lines.extend(["", "## Key gaps", ""])
    lines.extend(
        f"- `{item.obligation_id}`: `{item.status}` ({', '.join(item.missing_dimensions)})"
        for item in report.key_gaps
    )
    lines.extend(["", "## Diagnostics", ""])
    lines.extend(
        f"- `{item.code}` ({item.severity}): {item.message}"
        + (f" — `{item.path}`" if item.path else "")
        for item in report.diagnostics
    )
    return "\n".join(lines)
