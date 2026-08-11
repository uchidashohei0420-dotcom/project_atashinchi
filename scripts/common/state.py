import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "srsltid",
}


def canonicalize_url(url: str) -> str:
    """Normalize a URL so re-runs recognize the same item: strip tracking
    params and fragments, drop trailing slashes from the path."""
    parts = urlsplit(url.strip())
    query_pairs = [
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in _TRACKING_PARAMS
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme, parts.netloc, path, urlencode(query_pairs), ""))


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path, data):
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp_path, path)


def _parse_ts(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def prune_dict_older_than(items: dict, days: int, timestamp_key: str = "first_seen", now=None) -> dict:
    """Drop entries of a {url: {..., timestamp_key: iso_str}} map older than `days`."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    kept = {}
    for key, value in items.items():
        ts = _parse_ts(value.get(timestamp_key))
        if ts is None or ts >= cutoff:
            kept[key] = value
    return kept


def prune_list_older_than(items: list, days: int, timestamp_key: str = "detected_at", now=None) -> list:
    """Drop entries of a [{..., timestamp_key: iso_str}] list older than `days`."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    kept = []
    for item in items:
        ts = _parse_ts(item.get(timestamp_key))
        if ts is None or ts >= cutoff:
            kept.append(item)
    return kept
