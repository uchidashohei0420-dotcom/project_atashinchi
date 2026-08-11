from pathlib import Path

from scripts.adapters import keraeiko, shinei_shop, shopnui

FIXTURES = Path(__file__).parent / "fixtures"


def test_shopnui_parse_extracts_items():
    html = (FIXTURES / "shopnui_sample.html").read_text(encoding="utf-8")
    items = shopnui.parse(html)
    assert len(items) == 5
    first = items[0]
    assert first.url.startswith("https://www.shopnui.jp/shopdetail/")
    assert "あたしンち" in first.title


def test_shopnui_parse_dedupes_by_url():
    html = (FIXTURES / "shopnui_sample.html").read_text(encoding="utf-8")
    items = shopnui.parse(html)
    urls = [i.url for i in items]
    assert len(urls) == len(set(urls))


def test_shopnui_parse_empty_page_returns_empty_list():
    assert shopnui.parse("<html><body>no products here</body></html>") == []


def test_keraeiko_parse_extracts_items():
    html = (FIXTURES / "keraeiko_sample.html").read_text(encoding="utf-8")
    items = keraeiko.parse(html)
    assert len(items) == 3
    assert items[0].url == "https://keraeiko.com/1688.html"
    assert items[0].title == "『あたしンちSUPER』④巻、発売！"


def test_keraeiko_parse_empty_page_returns_empty_list():
    assert keraeiko.parse("<html><body>nothing</body></html>") == []


def test_shinei_shop_parse_filters_to_atashinchi_only():
    html = (FIXTURES / "shinei_shop_sample.html").read_text(encoding="utf-8")
    items = shinei_shop.parse(html)
    # fixture has 12 posts total, only 2 mention あたしンち
    assert len(items) == 2
    assert all("あたしンち" in i.title for i in items)


def test_shinei_shop_parse_excludes_other_franchises():
    html = (FIXTURES / "shinei_shop_sample.html").read_text(encoding="utf-8")
    items = shinei_shop.parse(html)
    titles = [i.title for i in items]
    assert not any("モルカー" in t for t in titles)
    assert not any("銀河特急" in t for t in titles)


def test_shinei_shop_parse_empty_page_returns_empty_list():
    assert shinei_shop.parse("<html><body>nothing</body></html>") == []
