from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scripts.adapters.base import fetch_html
from scripts.common.models import Item

SOURCE_ID = "shopnui"
SOURCE_LABEL = "shopぬい"

BASE_URL = "https://www.shopnui.jp"
LIST_URL = "https://www.shopnui.jp/shopbrand/ct290/"


def fetch() -> List[Item]:
    html = fetch_html(LIST_URL, encoding="euc-jp")
    return parse(html)


def parse(html: str) -> List[Item]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Item] = []
    seen_urls = set()
    for link in soup.select("ul.innerList p.name a"):
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
