from datetime import datetime, timedelta, timezone

from scripts.common.state import (
    canonicalize_url,
    load_json,
    prune_dict_older_than,
    prune_list_older_than,
    save_json_atomic,
)


def test_canonicalize_url_strips_tracking_params_and_fragment():
    assert canonicalize_url(
        "https://example.com/goods/1/?utm_source=x&id=1#top"
    ) == "https://example.com/goods/1?id=1"


def test_canonicalize_url_normalizes_trailing_slash():
    assert canonicalize_url("https://example.com/news/") == canonicalize_url(
        "https://example.com/news"
    )


def test_save_and_load_json_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    data = {"a": 1, "b": {"c": 2}}
    save_json_atomic(path, data)
    assert load_json(path, default={}) == data


def test_load_json_missing_file_returns_default(tmp_path):
    path = tmp_path / "missing.json"
    assert load_json(path, default={"x": []}) == {"x": []}


def test_save_json_atomic_leaves_no_tmp_file(tmp_path):
    path = tmp_path / "state.json"
    save_json_atomic(path, {"a": 1})
    assert not (tmp_path / "state.json.tmp").exists()


def test_prune_dict_older_than_drops_stale_entries():
    now = datetime(2026, 8, 11, tzinfo=timezone.utc)
    items = {
        "old": {"title": "old", "first_seen": (now - timedelta(days=91)).isoformat()},
        "recent": {"title": "recent", "first_seen": (now - timedelta(days=10)).isoformat()},
    }
    kept = prune_dict_older_than(items, days=90, now=now)
    assert list(kept.keys()) == ["recent"]


def test_prune_list_older_than_drops_stale_entries():
    now = datetime(2026, 8, 11, tzinfo=timezone.utc)
    items = [
        {"title": "old", "detected_at": (now - timedelta(days=91)).isoformat()},
        {"title": "recent", "detected_at": (now - timedelta(days=10)).isoformat()},
    ]
    kept = prune_list_older_than(items, days=90, now=now)
    assert [i["title"] for i in kept] == ["recent"]


def test_prune_keeps_entries_missing_timestamp():
    items = {"no_ts": {"title": "no timestamp"}}
    kept = prune_dict_older_than(items, days=90)
    assert kept == items
