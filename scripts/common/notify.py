from datetime import datetime
from typing import List

from scripts.common import config


def format_immediate(title: str, url: str, source_label: str, when_iso: str) -> str:
    when = datetime.fromisoformat(when_iso).astimezone(config.JST)
    return f"{title}\n{url}\n{source_label} / {when.strftime('%m/%d %H:%M')}"


def format_digest(pending: List[dict]) -> str:
    """Combine queued high-confidence overflow (throttled) and low-confidence
    finds into a single daily digest message."""
    if not pending:
        return ""
    high = [p for p in pending if p["tier"] == "high"]
    low = [p for p in pending if p["tier"] == "low"]

    lines = ["【本日のダイジェスト】"]
    if high:
        lines.append("\n🍊 熟した実（通知枠の都合でまとめ送信）")
        for p in high:
            lines.append(f"・{p['title']}\n  {p['url']}\n  {p.get('source_label', p.get('source', ''))}")
    if low:
        lines.append("\n🌱 青い実（要確認）")
        for p in low:
            lines.append(f"・{p['title']}\n  {p['url']}\n  検索: {p.get('query', '')}")
    return "\n".join(lines)
