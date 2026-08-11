from scripts.common.models import Item
from scripts.run_low_confidence import process_search_results


def test_first_run_records_baseline_without_queueing():
    items = [Item(url="https://example.com/a", title="A", query="あたしンち グッズ")]
    seen_items, digest_queue = process_search_results(items, {}, {"pending": []}, "2026-08-11T06:00:00+09:00")
    assert digest_queue["pending"] == []
    assert len(seen_items["google_search"]) == 1


def test_second_run_queues_new_items_as_low_tier():
    existing = {"https://example.com/a": {"title": "A", "query": "q", "first_seen": "2026-08-01T06:00:00+09:00"}}
    items = [
        Item(url="https://example.com/a", title="A", query="あたしンち グッズ"),
        Item(url="https://example.com/b", title="B", query="あたしンち イベント"),
    ]
    seen_items, digest_queue = process_search_results(
        items, {"google_search": existing}, {"pending": []}, "2026-08-11T06:00:00+09:00"
    )
    assert len(digest_queue["pending"]) == 1
    entry = digest_queue["pending"][0]
    assert entry["tier"] == "low"
    assert entry["url"] == "https://example.com/b"
    assert entry["query"] == "あたしンち イベント"


def test_all_new_items_queue_with_no_throttle_concept():
    # process_search_results has no quota parameter at all: every genuinely
    # new low-confidence item always queues for the digest, unlike the
    # high-confidence tier's throttle-then-digest-overflow logic.
    existing = {"https://example.com/seed": {"title": "seed", "query": "q", "first_seen": "2026-08-01T06:00:00+09:00"}}
    items = [
        Item(url="https://example.com/1", title="one", query="あたしンち グッズ"),
        Item(url="https://example.com/2", title="two", query="あたしンち イベント"),
        Item(url="https://example.com/3", title="three", query="あたしンち 予約"),
    ]
    seen_items, digest_queue = process_search_results(
        items, {"google_search": existing}, {"pending": []}, "2026-08-11T06:00:00+09:00"
    )
    assert len(digest_queue["pending"]) == 3
    assert all(p["tier"] == "low" for p in digest_queue["pending"])
