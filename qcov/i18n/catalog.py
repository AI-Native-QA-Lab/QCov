"""Small built-in message catalog for the MVP CLI and reports."""

from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    "dimension.behavior": {"en": "Behavior", "zh-CN": "行为"},
    "dimension.boundary": {"en": "Boundary", "zh-CN": "边界"},
    "dimension.data": {"en": "Data", "zh-CN": "数据"},
    "dimension.concurrency": {"en": "Concurrency", "zh-CN": "并发"},
    "dimension.idempotency": {"en": "Idempotency", "zh-CN": "幂等性"},
    "dimension.production": {"en": "Production", "zh-CN": "生产环境"},
    "dimension.security": {"en": "Security", "zh-CN": "安全"},
    "dimension.fault": {"en": "Fault", "zh-CN": "故障"},
    "dimension.integration": {"en": "Integration", "zh-CN": "集成"},
    "label.required": {"en": "Required evidence", "zh-CN": "所需证据"},
    "label.observed": {"en": "Observed evidence", "zh-CN": "已观测证据"},
    "label.unproven": {"en": "Unproven dimensions", "zh-CN": "未证实维度"},
    "label.status": {"en": "Status", "zh-CN": "状态"},
    "delta.title": {"en": "PR Quality Coverage Delta", "zh-CN": "PR 质量覆盖增量"},
    "delta.base": {"en": "Base commit", "zh-CN": "基线提交"},
    "delta.head": {"en": "Head commit", "zh-CN": "目标提交"},
    "delta.change": {"en": "Change", "zh-CN": "变更"},
    "delta.before": {"en": "Before status", "zh-CN": "变更前状态"},
    "delta.after": {"en": "After status", "zh-CN": "变更后状态"},
    "delta.evidence": {"en": "Changed evidence", "zh-CN": "变更的证据"},
    "policy.id": {"en": "Policy", "zh-CN": "策略"},
    "policy.evaluated_at": {"en": "Evaluated at", "zh-CN": "评估时间"},
    "policy.coverage_status": {"en": "Coverage status", "zh-CN": "覆盖状态"},
    "policy.decision": {"en": "Policy decision", "zh-CN": "策略决定"},
    "policy.violations": {"en": "Violations", "zh-CN": "违规"},
    "policy.waiver": {"en": "Waiver", "zh-CN": "豁免"},
    "policy.reason": {"en": "Reason", "zh-CN": "理由"},
    "policy.expires_at": {"en": "Expires at", "zh-CN": "到期时间"},
    "policy.approved_by": {"en": "Approved by", "zh-CN": "批准人"},
    "policy.expired_waiver_cleanup": {"en": "Expired waiver: remove or renew it.", "zh-CN": "豁免已过期：请删除或续期。"},
    "mapping.preview_title": {"en": "Evidence mapping preview", "zh-CN": "证据映射预览"},
    "mapping.ids": {"en": "Mapping ids", "zh-CN": "映射 ID"},
    "mapping.evidence": {"en": "Mapped evidence", "zh-CN": "映射证据"},
    "mapping.diagnostics": {"en": "Mapping diagnostics", "zh-CN": "映射诊断"},
}


def translate(key: str, locale: str = "en") -> str:
    """Translate a presentation key while preserving stable protocol values."""
    return MESSAGES.get(key, {}).get(locale, MESSAGES.get(key, {}).get("en", key))
