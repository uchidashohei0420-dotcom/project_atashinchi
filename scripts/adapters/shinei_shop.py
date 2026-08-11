from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scripts.adapters.base import fetch_html
from scripts.common.models import Item

SOURCE_ID = "shinei_shop"
SOURCE_LABEL = "シンエイ ONLINE STORE"

BASE_URL = "https://shinei-shop.com"
LIST_URL = "https://shinei-shop.com/blogs/%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9"

# This blog is shared across every Shin-Ei Animation property (Molcar, Ginga
# Tokkyu, etc.), not just Atashinchi, unlike the other two adapters' listings
# which are already scoped to Atashinchi. Without this filter every unrelated
# franchise post would trigger a notification.
TITLE_FILTER = "あたしンち"


def fetch() -> List[Item]:
    html = fetch_html(LIST_URL)
    return parse(html)


def parse(html: str) -> List[Item]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Item] = []
    seen_urls = set()
    for link in soup.select("a.column"):
        href = link.get("href")
        title_el = link.select_one("p.entry_tit")
        if not href or not title_el:
            continue
        title = title_el.get_text(strip=True)
        if TITLE_FILTER not in title:
            continue
        url = urljoin(BASE_URL, href)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        items.append(Item(url=url, title=title))
    return items


if __name__ == "__main__":
    for item in fetch():
        print(item)
