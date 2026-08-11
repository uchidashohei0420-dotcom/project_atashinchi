import re
from datetime import datetime

from scripts.common.config import JST
from scripts.site_generator import render

NOW = datetime(2026, 8, 11, 14, 30, tzinfo=JST)


def test_render_leaves_no_unreplaced_tokens():
    output = render({}, {"year_month": "2026-08", "count": 0}, now=NOW)
    assert not re.search(r"\{\{[A-Z_]+\}\}", output)


def test_render_shows_empty_state_when_no_items():
    output = render({}, {"year_month": "2026-08", "count": 0}, now=NOW)
    assert output.count("まだ検知した項目はありません。") == 2


def test_render_includes_high_confidence_entry():
    seen_items = {
        "shopnui": {
            "https://www.shopnui.jp/shopdetail/1/": {
                "title": "あたしンちぬいぐるみ",
                "first_seen": "2026-08-11T14:02:00+09:00",
            }
        }
    }
    output = render(seen_items, {"year_month": "2026-08", "count": 0}, now=NOW)
    assert "あたしンちぬいぐるみ" in output
    assert "shopぬい" in output
    assert "08/11 14:02" in output


def test_render_includes_low_confidence_entry_with_query_badge():
    seen_items = {
        "google_search": {
            "https://example.com/news": {
                "title": "コラボの噂",
                "query": "あたしンち イベント",
                "first_seen": "2026-08-11T06:00:00+09:00",
            }
        }
    }
    output = render(seen_items, {"year_month": "2026-08", "count": 0}, now=NOW)
    assert "コラボの噂" in output
    assert "検索: あたしンち イベント" in output
    assert "未確認" in output


def test_render_escapes_html_in_titles():
    seen_items = {
        "shopnui": {
            "https://example.com/x": {
                "title": "<script>alert(1)</script>",
                "first_seen": "2026-08-11T14:02:00+09:00",
            }
        }
    }
    output = render(seen_items, {"year_month": "2026-08", "count": 0}, now=NOW)
    assert "<script>alert(1)</script>" not in output
    assert "&lt;script&gt;" in output


def test_render_shows_quota_warn_class_above_threshold():
    output = render({}, {"year_month": "2026-08", "count": 185}, now=NOW)
    assert "quota-warn" in output
    assert "185 / 200" in output


def test_render_keeps_font_face_intact():
    output = render({}, {"year_month": "2026-08", "count": 0}, now=NOW)
    assert output.count("@font-face") == 2
    assert "base64" in output
