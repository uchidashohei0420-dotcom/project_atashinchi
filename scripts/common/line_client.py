import logging

import requests

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
MAX_TEXT_LENGTH = 5000
TIMEOUT = 15

logger = logging.getLogger(__name__)


def push_text(user_id: str, token: str, text: str, dry_run: bool = False) -> bool:
    """Send a single LINE push message. In dry-run mode, logs instead of calling
    the API so local dev / workflow_dispatch smoke tests never spend the
    monthly free quota. Returns True on success (dry-run always succeeds)."""
    text = text[:MAX_TEXT_LENGTH]
    if dry_run:
        logger.info("[DRY_RUN] LINE push skipped:\n%s", text)
        return True

    resp = requests.post(
        LINE_PUSH_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"to": user_id, "messages": [{"type": "text", "text": text}]},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return True
