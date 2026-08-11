import html
from datetime import datetime
from typing import List, Optional

from scripts.common import config

HIGH_CONFIDENCE_SOURCES = ("keraeiko", "shinei_shop", "shopnui")

ENTRY_RIPE_TEMPLATE = """    <a class="entry" href="{url}">
      <span class="entry-dot"></span>
      <div>
        <p class="entry-title">{title}</p>
        <div class="entry-meta">
          <span class="source-badge">{source_label}</span>
          <span class="entry-time">{time}</span>
        </div>
      </div>
      <span class="entry-arrow">↗</span>
    </a>"""

ENTRY_UNRIPE_TEMPLATE = """    <a class="entry" href="{url}">
      <span class="entry-dot"></span>
      <div>
        <p class="entry-title">{title} <span class="low-conf-tag">未確認</span></p>
        <div class="entry-meta">
          <span class="source-badge">検索: {query}</span>
          <span class="entry-time">{time}</span>
        </div>
      </div>
      <span class="entry-arrow">↗</span>
    </a>"""

EMPTY_STATE = '    <p class="empty-state">まだ検知した項目はありません。</p>'


def _format_time(iso_str: str) -> str:
    if not iso_str:
        return ""
    dt = datetime.fromisoformat(iso_str)
    dt = dt.astimezone(config.JST)
    return dt.strftime("%m/%d %H:%M")


def _collect_ripe_entries(seen_items: dict, limit: int = 100) -> List[dict]:
    entries = []
    for source_id in HIGH_CONFIDENCE_SOURCES:
        for url, entry in seen_items.get(source_id, {}).items():
            entries.append({
                "url": url,
                "title": entry.get("title", ""),
                "source_label": config.SOURCE_LABELS.get(source_id, source_id),
                "first_seen": entry.get("first_seen", ""),
            })
    entries.sort(key=lambda e: e["first_seen"], reverse=True)
    return entries[:limit]


def _collect_unripe_entries(seen_items: dict, limit: int = 100) -> List[dict]:
    entries = []
    for url, entry in seen_items.get("google_search", {}).items():
        entries.append({
            "url": url,
            "title": entry.get("title", ""),
            "query": entry.get("query", ""),
            "first_seen": entry.get("first_seen", ""),
        })
    entries.sort(key=lambda e: e["first_seen"], reverse=True)
    return entries[:limit]


def _render_ripe_entries(entries: List[dict]) -> str:
    if not entries:
        return EMPTY_STATE
    return "\n".join(
        ENTRY_RIPE_TEMPLATE.format(
            url=html.escape(e["url"]),
            title=html.escape(e["title"]),
            source_label=html.escape(e["source_label"]),
            time=_format_time(e["first_seen"]),
        )
        for e in entries
    )


def _render_unripe_entries(entries: List[dict]) -> str:
    if not entries:
        return EMPTY_STATE
    return "\n".join(
        ENTRY_UNRIPE_TEMPLATE.format(
            url=html.escape(e["url"]),
            title=html.escape(e["title"]),
            query=html.escape(e["query"]),
            time=_format_time(e["first_seen"]),
        )
        for e in entries
    )


def render(seen_items: dict, quota: dict, now: Optional[datetime] = None) -> str:
    """Render the full site HTML by token-replacing into the static template.
    Uses str.replace (not str.format) because the template's CSS block is
    full of literal `{`/`}` that would collide with format-string syntax."""
    now = now or config.now_jst()
    template = config.SITE_TEMPLATE_PATH.read_text(encoding="utf-8")

    ripe_entries = _collect_ripe_entries(seen_items)
    unripe_entries = _collect_unripe_entries(seen_items)

    quota_count = quota.get("count", 0)
    quota_percent = min(100, round(quota_count / config.MONTHLY_LINE_CAP * 100))
    quota_warn_class = " quota-warn" if quota_count >= config.THROTTLE_THRESHOLD else ""

    replacements = {
        "{{LAST_CHECKED}}": now.strftime("%m/%d %H:%M"),
        "{{SITE_COUNT}}": str(len(HIGH_CONFIDENCE_SOURCES)),
        "{{QUOTA_COUNT}}": str(quota_count),
        "{{QUOTA_CAP}}": str(config.MONTHLY_LINE_CAP),
        "{{QUOTA_PERCENT}}": str(quota_percent),
        "{{QUOTA_WARN_CLASS}}": quota_warn_class,
        "{{RETENTION_DAYS}}": str(config.RETENTION_DAYS),
        "{{RIPE_COUNT}}": str(len(ripe_entries)),
        "{{UNRIPE_COUNT}}": str(len(unripe_entries)),
        "{{RIPE_ENTRIES}}": _render_ripe_entries(ripe_entries),
        "{{UNRIPE_ENTRIES}}": _render_unripe_entries(unripe_entries),
        "{{REPO_URL}}": config.REPO_URL,
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template


def generate(seen_items: dict, quota: dict, now: Optional[datetime] = None) -> None:
    output = render(seen_items, quota, now=now)
    config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    config.SITE_OUTPUT_PATH.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    from scripts.common.state import load_json

    seen = load_json(config.SEEN_ITEMS_PATH, default={})
    quota = load_json(config.LINE_QUOTA_PATH, default={"year_month": "", "count": 0})
    generate(seen, quota)
