import logging

from scripts import google_search, site_generator
from scripts.common import config, notify
from scripts.common.health import record_failure, record_success
from scripts.common.line_client import get_access_token_or_dry_run, push_text
from scripts.common.quota import increment, load_or_reset_month
from scripts.common.state import (
    canonicalize_url,
    load_json,
    prune_dict_older_than,
    prune_list_older_than,
    save_json_atomic,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def process_search_results(items, seen_items, digest_queue, now_iso):
    """Diff Google Custom Search results against the seen-registry. Unlike
    the high-confidence tier, low-confidence items are NEVER pushed
    immediately - every genuinely new one is queued for the daily digest.
    First-ever run is a silent baseline, same as the high-confidence tier."""
    source_seen = dict(seen_items.get(google_search.SOURCE_ID, {}))
    is_first_run = len(source_seen) == 0

    for item in items:
        canon = canonicalize_url(item.url)
        if canon in source_seen:
            continue
        source_seen[canon] = {"title": item.title, "query": item.query, "first_seen": now_iso}
        if is_first_run:
            continue
        digest_queue["pending"].append({
            "tier": "low",
            "source": google_search.SOURCE_ID,
            "query": item.query,
            "title": item.title,
            "url": item.url,
            "detected_at": now_iso,
        })

    seen_items = dict(seen_items)
    seen_items[google_search.SOURCE_ID] = source_seen
    return seen_items, digest_queue


def run():
    now = config.now_jst()
    now_iso = now.isoformat()
    line_token = get_access_token_or_dry_run(config.LINE_CHANNEL_ID, config.LINE_CHANNEL_SECRET, config.DRY_RUN)

    seen_items = load_json(config.SEEN_ITEMS_PATH, default={})
    quota = load_json(config.LINE_QUOTA_PATH, default={"year_month": "", "count": 0})
    health = load_json(config.SITE_HEALTH_PATH, default={})
    digest_queue = load_json(config.DIGEST_QUEUE_PATH, default={"pending": []})

    quota = load_or_reset_month(quota, now)

    for source_id in list(seen_items.keys()):
        seen_items[source_id] = prune_dict_older_than(seen_items[source_id], config.RETENTION_DAYS, now=now)
    digest_queue["pending"] = prune_list_older_than(digest_queue["pending"], config.RETENTION_DAYS, now=now)

    try:
        items = google_search.fetch(config.GOOGLE_API_KEY, config.GOOGLE_CSE_ID, config.SEARCH_QUERIES)
    except Exception as exc:  # noqa: BLE001 - a failed search run must not crash the workflow
        logger.exception("google_search failed")
        health, alert = record_failure(
            health, google_search.SOURCE_ID, google_search.SOURCE_LABEL, str(exc), now_iso
        )
        if alert:
            push_text(config.LINE_USER_ID, line_token, alert, dry_run=config.DRY_RUN)
        items = []
    else:
        health, alert = record_success(health, google_search.SOURCE_ID, google_search.SOURCE_LABEL)
        if alert:
            push_text(config.LINE_USER_ID, line_token, alert, dry_run=config.DRY_RUN)

    seen_items, digest_queue = process_search_results(items, seen_items, digest_queue, now_iso)
    logger.info("google_search: fetched=%d pending_digest=%d", len(items), len(digest_queue["pending"]))

    if digest_queue["pending"]:
        digest_text = notify.format_digest(digest_queue["pending"])
        try:
            push_text(config.LINE_USER_ID, line_token, digest_text, dry_run=config.DRY_RUN)
        except Exception:  # noqa: BLE001 - keep the queue intact so it retries tomorrow
            logger.exception("digest push failed; leaving queue intact for retry")
        else:
            quota = increment(quota)
            digest_queue["pending"] = []

    save_json_atomic(config.SEEN_ITEMS_PATH, seen_items)
    save_json_atomic(config.LINE_QUOTA_PATH, quota)
    save_json_atomic(config.SITE_HEALTH_PATH, health)
    save_json_atomic(config.DIGEST_QUEUE_PATH, digest_queue)

    site_generator.generate(seen_items, quota, now=now)


if __name__ == "__main__":
    run()
