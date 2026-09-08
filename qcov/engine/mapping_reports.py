"""Reports for mapped evidence preview and diagnostics."""

from __future__ import annotations

import json
from collections.abc import Sequence

from qcov.engine.mapping import MappingDiagnostic, MappingMaterialization
from qcov.i18n.catalog import translate
from qcov.models.protocol import QualityEvidence


def _diagnostic_dict(item: MappingDiagnostic) -> dict[str, object]:
    payload: dict[str, object] = {"code": item.code, "message": item.message}
    if item.mapping_id is not None:
        payload["mappingId"] = item.mapping_id
    if item.producer is not None:
        payload["producer"] = item.producer
    if item.identity is not None:
        payload["identity"] = item.identity
    if item.artifact_path is not None:
        payload["artifactPath"] = item.artifact_path
    return payload


def _format_diagnostic_line(diagnostic: MappingDiagnostic) -> str:
    detail = diagnostic.message
    if diagnostic.identity:
        detail = f"{detail} ({diagnostic.producer}:{diagnostic.identity})"
    elif diagnostic.artifact_path:
        detail = f"{detail} ({diagnostic.artifact_path})"
    return f"- `{diagnostic.code}`: {detail}"


def _preview_evidence_dict(item: QualityEvidence) -> dict[str, object]:
    return {
        "artifactPath": item.artifact.path,
        "dimension": item.evidence.dimension.value,
        "evidenceId": item.metadata.id,
        "executionStatus": item.execution.status,
        "obligationRef": item.obligation.ref,
        "producer": item.producer.name,
        "type": item.evidence.type,
    }


def render_map_preview_json(materialization: MappingMaterialization) -> str:
    """Stable English-keyed preview of mapped evidence."""
    return json.dumps(
        {
            "diagnostics": [_diagnostic_dict(item) for item in materialization.diagnostics],
            "evidence": [_preview_evidence_dict(item) for item in materialization.evidence],
            "mappingIds": list(materialization.mapping_ids),
        },
        indent=2,
        sort_keys=True,
    )


def render_map_preview_markdown(materialization: MappingMaterialization, locale: str = "en") -> str:
    """Localized Markdown preview of mapped evidence."""
    blocks = [f"## {translate('mapping.preview_title', locale)}"]
    blocks.append(
        f"{translate('mapping.ids', locale)}: "
        + (", ".join(materialization.mapping_ids) or "—")
    )
    blocks.append(f"### {translate('mapping.evidence', locale)}")
    if materialization.evidence:
        for evidence in materialization.evidence:
            blocks.append(
                f"- `{evidence.metadata.id}` → `{evidence.obligation.ref}` / "
                f"`{evidence.evidence.dimension.value}` / `{evidence.evidence.type}` / "
                f"`{evidence.execution.status}` / `{evidence.producer.name}` / `{evidence.artifact.path}`"
            )
    else:
        blocks.append("- —")
    blocks.append(f"### {translate('mapping.diagnostics', locale)}")
    if materialization.diagnostics:
        for diagnostic in materialization.diagnostics:
            blocks.append(_format_diagnostic_line(diagnostic))
    else:
        blocks.append("- —")
    return "\n\n".join(blocks)


def append_mapping_diagnostics_json(
    payload: dict[str, object], diagnostics: Sequence[MappingDiagnostic]
) -> dict[str, object]:
    """Attach stable mappingDiagnostics when mapping was applied."""
    updated = dict(payload)
    updated["mappingDiagnostics"] = [_diagnostic_dict(item) for item in diagnostics]
    return updated


def render_mapping_diagnostics_markdown(
    diagnostics: Sequence[MappingDiagnostic], locale: str = "en"
) -> str:
    """Always render the mapping diagnostics section when mapping was applied."""
    lines = [f"## {translate('mapping.diagnostics', locale)}", ""]
    if diagnostics:
        lines.extend(_format_diagnostic_line(item) for item in diagnostics)
    else:
        lines.append("- —")
    return "\n".join(lines)
