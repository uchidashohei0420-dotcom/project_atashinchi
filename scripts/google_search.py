from typing import List

import requests

from scripts.common.models import Item

SOURCE_ID = "google_search"
SOURCE_LABEL = "Google検索"

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
TIMEOUT = 15


def search(query: str, api_key: str, cse_id: str) -> List[Item]:
    resp = requests.get(
        SEARCH_URL,
        params={"key": api_key, "cx": cse_id, "q": query, "num": 10},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    items: List[Item] = []
    for result in data.get("items", []):
        link = result.get("link")
        title = result.get("title")
        if not link or not title:
            continue
        items.append(Item(url=link, title=title, query=query))
    return items


def fetch(api_key: str, cse_id: str, queries: List[str]) -> List[Item]:
    """Run every configured keyword query and dedupe results across queries
    by URL (keeping the first query that surfaced each URL)."""
    items: List[Item] = []
    seen_urls = set()
    for query in queries:
        for item in search(query, api_key, cse_id):
            if item.url in seen_urls:
                continue
            seen_urls.add(item.url)
            items.append(item)
    return items
