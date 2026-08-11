import logging

from scripts import site_generator
from scripts.adapters import keraeiko, shinei_shop, shopnui
from scripts.common import config, notify
from scripts.common.health import record_failure, record_success
from scripts.common.line_client import get_access_token_or_dry_run, push_text
from scripts.common.quota import increment, is_throttled, load_or_reset_month
from scripts.common.state import (
    canonicalize_url,
    load_json,
    prune_dict_older_than,
    prune_list_older_than,
    save_json_atomic,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ADAPTERS = [keraeiko, shinei_shop, shopnui]


def process_source(source_id, source_label, items, seen_items, quota, digest_queue, now_iso, dry_run, line_token=""):
    """Diff fetched items against the seen-registry for one source. Genuinely
    new items are pushed immediately unless the monthly quota is throttled,
    in which case they're queued for the daily digest instead. The very
    first run for a source (empty registry) only records a baseline and
    never notifies."""
    source_seen = dict(seen_items.get(source_id, {}))
    is_first_run = len(source_seen) == 0
    sent = 0

    for item in items:
        canon = canonicalize_url(item.url)
        if canon in source_seen:
            continue
        source_seen[canon] = {"title": item.title, "first_seen": now_iso}
        if is_first_run:
            continue
        if not is_throttled(quota, config.THROTTLE_THRESHOLD):
            text = notify.format_immediate(item.title, item.url, source_label, now_iso)
            push_text(config.LINE_USER_ID, line_token, text, dry_run=dry_run)
            quota = increment(quota)
            sent += 1
        else:
            digest_queue["pending"].append({
                "tier": "high",
                "source": source_id,
                "source_label": source_label,
                "title": item.title,
                "url": item.url,
                "detected_at": now_iso,
            })

    seen_items = dict(seen_items)
    seen_items[source_id] = source_seen
    return seen_items, quota, digest_queue, sent


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

    for adapter in ADAPTERS:
        source_id = adapter.SOURCE_ID
        source_label = adapter.SOURCE_LABEL
        try:
            items = adapter.fetch()
        except Exception as exc:  # noqa: BLE001 - any adapter failure must not crash the run
            logger.exception("adapter %s failed", source_id)
            health, alert = record_failure(health, source_id, source_label, str(exc), now_iso)
            if alert:
                push_text(config.LINE_USER_ID, line_token, alert, dry_run=config.DRY_RUN)
            continue

        health, alert = record_success(health, source_id, source_label)
        if alert:
            push_text(config.LINE_USER_ID, line_token, alert, dry_run=config.DRY_RUN)

        seen_items, quota, digest_queue, sent = process_source(
            source_id, source_label, items, seen_items, quota, digest_queue, now_iso, config.DRY_RUN,
            line_token=line_token,
        )
        logger.info("%s: fetched=%d sent=%d", source_id, len(items), sent)

    save_json_atomic(config.SEEN_ITEMS_PATH, seen_items)
    save_json_atomic(config.LINE_QUOTA_PATH, quota)
    save_json_atomic(config.SITE_HEALTH_PATH, health)
    save_json_atomic(config.DIGEST_QUEUE_PATH, digest_queue)

    site_generator.generate(seen_items, quota, now=now)


if __name__ == "__main__":
    run()
