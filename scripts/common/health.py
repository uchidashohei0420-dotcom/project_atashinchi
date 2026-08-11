from typing import Optional, Tuple

"""Per-source failure/recovery tracking. Alerts fire only on a state
transition (ok->error or error->ok) so a persistently broken parser doesn't
spam a LINE alert on every 15-minute run and burn through the monthly quota."""

_DEFAULT_ENTRY = {"status": "ok", "last_error": None, "last_error_at": None}


def record_success(health: dict, source_id: str, source_label: str) -> Tuple[dict, Optional[str]]:
    entry = health.get(source_id, _DEFAULT_ENTRY)
    alert = None
    if entry.get("status") == "error":
        alert = f"✅ 復旧: {source_label}の取得が正常に戻りました"
    updated = dict(health)
    updated[source_id] = {"status": "ok", "last_error": None, "last_error_at": None}
    return updated, alert


def record_failure(
    health: dict, source_id: str, source_label: str, error_message: str, now_iso: str
) -> Tuple[dict, Optional[str]]:
    entry = health.get(source_id, _DEFAULT_ENTRY)
    alert = None
    if entry.get("status") != "error":
        alert = f"⚠️ 監視エラー: {source_label}の取得に失敗しました ({error_message})"
    updated = dict(health)
    updated[source_id] = {
        "status": "error",
        "last_error": error_message,
        "last_error_at": now_iso,
    }
    return updated, alert
