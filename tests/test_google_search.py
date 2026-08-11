import json
from pathlib import Path

from scripts.google_search import SEARCH_URL, fetch, search

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE = json.loads((FIXTURES / "google_search_sample.json").read_text(encoding="utf-8"))


def test_search_parses_items_and_tags_query(requests_mock):
    requests_mock.get(SEARCH_URL, json=SAMPLE)
    items = search("あたしンち グッズ", "key", "cx")
    assert len(items) == 2
    assert items[0].url == "https://example.com/cafe-collab"
    assert items[0].query == "あたしンち グッズ"


def test_search_handles_response_with_no_items(requests_mock):
    requests_mock.get(SEARCH_URL, json={})
    assert search("あたしンち イベント", "key", "cx") == []


def test_fetch_dedupes_across_multiple_queries(requests_mock):
    requests_mock.get(SEARCH_URL, json=SAMPLE)
    items = fetch("key", "cx", queries=["あたしンち グッズ", "あたしンち イベント", "あたしンち 予約"])
    # same fixture returned for all 3 queries; URLs must be deduped
    assert len(items) == 2
    assert requests_mock.call_count == 3
