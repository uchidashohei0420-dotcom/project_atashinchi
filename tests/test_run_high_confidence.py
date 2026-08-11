from scripts.common.models import Item
from scripts.run_high_confidence import process_source


def test_first_run_records_baseline_without_notifying():
    items = [Item(url="https://example.com/a", title="A"), Item(url="https://example.com/b", title="B")]
    seen_items, quota, digest_queue, sent = process_source(
        "shopnui", "shopぬい", items, {}, {"year_month": "2026-08", "count": 0},
        {"pending": []}, "2026-08-11T14:00:00+09:00", dry_run=True,
    )
    assert sent == 0
    assert len(seen_items["shopnui"]) == 2
    assert digest_queue["pending"] == []
    assert quota["count"] == 0


def test_second_run_notifies_only_genuinely_new_items():
    existing = {"https://example.com/a": {"title": "A", "first_seen": "2026-08-01T00:00:00+09:00"}}
    items = [Item(url="https://example.com/a", title="A"), Item(url="https://example.com/b", title="B")]
    seen_items, quota, digest_queue, sent = process_source(
        "shopnui", "shopぬい", items, {"shopnui": existing}, {"year_month": "2026-08", "count": 0},
        {"pending": []}, "2026-08-11T14:00:00+09:00", dry_run=True,
    )
    assert sent == 1
    assert quota["count"] == 1
    assert set(seen_items["shopnui"].keys()) == {"https://example.com/a", "https://example.com/b"}
    assert digest_queue["pending"] == []


def test_throttled_overflow_routes_to_digest_queue():
    existing = {"https://example.com/seed": {"title": "seed", "first_seen": "2026-08-01T00:00:00+09:00"}}
    items = [
        Item(url="https://example.com/1", title="one"),
        Item(url="https://example.com/2", title="two"),
        Item(url="https://example.com/3", title="three"),
    ]
    seen_items, quota, digest_queue, sent = process_source(
        "shopnui", "shopぬい", items, {"shopnui": existing}, {"year_month": "2026-08", "count": 179},
        {"pending": []}, "2026-08-11T14:00:00+09:00", dry_run=True,
    )
    assert sent == 1
    assert quota["count"] == 180
    assert len(digest_queue["pending"]) == 2
    assert all(p["tier"] == "high" for p in digest_queue["pending"])


def test_url_canonicalization_prevents_duplicate_notification():
    existing = {"https://example.com/a": {"title": "A", "first_seen": "2026-08-01T00:00:00+09:00"}}
    items = [Item(url="https://example.com/a/?utm_source=x", title="A")]
    seen_items, quota, digest_queue, sent = process_source(
        "shopnui", "shopぬい", items, {"shopnui": existing}, {"year_month": "2026-08", "count": 0},
        {"pending": []}, "2026-08-11T14:00:00+09:00", dry_run=True,
    )
    assert sent == 0
    assert len(seen_items["shopnui"]) == 1
