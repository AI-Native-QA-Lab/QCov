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
}


def translate(key: str, locale: str = "en") -> str:
    """Translate a presentation key while preserving stable protocol values."""
    return MESSAGES.get(key, {}).get(locale, MESSAGES.get(key, {}).get("en", key))
