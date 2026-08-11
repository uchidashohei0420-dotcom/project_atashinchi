from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scripts.adapters.base import fetch_html
from scripts.common.models import Item

SOURCE_ID = "keraeiko"
SOURCE_LABEL = "けらえいこ公式サイト"

BASE_URL = "https://keraeiko.com"
LIST_URL = "https://keraeiko.com/"


def fetch() -> List[Item]:
    html = fetch_html(LIST_URL)
    return parse(html)


def parse(html: str) -> List[Item]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Item] = []
    seen_urls = set()
    for post in soup.select("div.featured-small-post"):
        link = post.select_one("a.koz-medium")
        if not link:
            continue
        href = link.get("href")
        title = link.get_text(strip=True)
        if not href or not title:
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
