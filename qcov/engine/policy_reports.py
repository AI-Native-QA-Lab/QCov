"""Stable JSON and localized Markdown policy reports."""

from __future__ import annotations

import json

from qcov.engine.policy import PolicyReport, PolicyResult
from qcov.i18n.catalog import translate


def _result_dict(result: PolicyResult) -> dict[str, object]:
    waiver: dict[str, str] | None = None
    if result.waiver is not None:
        waiver = {
            "obligationRef": result.waiver.obligation_ref,
            "reason": result.waiver.reason,
            "expiresAt": result.waiver.expires_at.isoformat(),
        }
        if result.waiver.approved_by is not None:
            waiver["approvedBy"] = result.waiver.approved_by
    return {
        "obligationId": result.obligation_id,
        "coverageStatus": result.coverage_status.value,
        "decision": result.decision.value,
        "violations": [violation.code for violation in result.violations],
        "waiver": waiver,
    }


def render_policy_json(report: PolicyReport) -> str:
    """Render a language-neutral policy report."""
    return json.dumps(
        {
            "policyId": report.policy_id,
            "evaluatedAt": report.evaluated_at.isoformat(),
            "results": [_result_dict(result) for result in report.results],
        },
        indent=2,
        sort_keys=True,
    )


def render_policy_markdown(report: PolicyReport, locale: str = "en") -> str:
    """Render a localized explainable policy report."""
    blocks = [
        (
            f"## {translate('policy.id', locale)}: {report.policy_id}\n\n"
            f"{translate('policy.evaluated_at', locale)}: {report.evaluated_at.isoformat()}"
        )
    ]
    for result in report.results:
        violations = ", ".join(item.code for item in result.violations) or "—"
        block = (
            f"### {result.obligation_id}\n\n"
            f"{translate('policy.coverage_status', locale)}: `{result.coverage_status.value}`\n\n"
            f"{translate('policy.decision', locale)}: `{result.decision.value}`\n\n"
            f"{translate('policy.violations', locale)}: {violations}"
        )
        if result.waiver is not None:
            waiver = result.waiver
            approver = f"; {translate('policy.approved_by', locale)}: {waiver.approved_by}" if waiver.approved_by else ""
            block += (
                f"\n\n{translate('policy.waiver', locale)}: {translate('policy.reason', locale)}: "
                f"{waiver.reason}; {translate('policy.expires_at', locale)}: "
                f"{waiver.expires_at.isoformat()}{approver}"
            )
        blocks.append(block)
    return "\n\n".join(blocks)
