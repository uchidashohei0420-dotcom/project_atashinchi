import sys

from scripts.common import config
from scripts.common.line_client import get_access_token_or_dry_run, push_text

DEFAULT_MESSAGE = "🔔 テスト通知: LINE連携は正常に動作しています"


def run(text: str = DEFAULT_MESSAGE) -> bool:
    token = get_access_token_or_dry_run(config.LINE_CHANNEL_ID, config.LINE_CHANNEL_SECRET, config.DRY_RUN)
    return push_text(config.LINE_USER_ID, token, text, dry_run=config.DRY_RUN)


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MESSAGE
    run(message)
