import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")

BASE_DIR = Path(__file__).resolve().parents[2]
STATE_DIR = BASE_DIR / "state"
DOCS_DIR = BASE_DIR / "docs"
TEMPLATES_DIR = BASE_DIR / "templates"

SEEN_ITEMS_PATH = STATE_DIR / "seen_items.json"
LINE_QUOTA_PATH = STATE_DIR / "line_quota.json"
SITE_HEALTH_PATH = STATE_DIR / "site_health.json"
DIGEST_QUEUE_PATH = STATE_DIR / "digest_queue.json"
SITE_TEMPLATE_PATH = TEMPLATES_DIR / "site_template.html"
SITE_OUTPUT_PATH = DOCS_DIR / "index.html"

RETENTION_DAYS = 90
MONTHLY_LINE_CAP = 200
THROTTLE_THRESHOLD = 180

LINE_CHANNEL_ID = os.environ.get("LINE_CHANNEL_ID", "")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_USER_ID = os.environ.get("LINE_USER_ID", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")
DRY_RUN = os.environ.get("DRY_RUN", "false").strip().lower() in ("1", "true", "yes")

SOURCE_LABELS = {
    "keraeiko": "けらえいこ公式サイト",
    "shinei_shop": "シンエイ ONLINE STORE",
    "shopnui": "shopぬい",
    "google_search": "Google検索",
}

SEARCH_QUERIES = ["あたしンち グッズ", "あたしンち イベント", "あたしンち 予約"]

GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
REPO_URL = f"https://github.com/{GITHUB_REPOSITORY}" if GITHUB_REPOSITORY else "#"


def now_jst() -> datetime:
    return datetime.now(JST)


def now_iso() -> str:
    return now_jst().isoformat()
