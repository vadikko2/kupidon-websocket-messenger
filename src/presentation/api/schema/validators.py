import functools
import re

import fastapi

AccountId = functools.partial(
    fastapi.Header,
    default=None,
    description="Target account ID",
    alias="AccountID",
    example="account-id",
)


class EmojiValidationError(Exception):
    def __init__(self, emoji: str) -> None:
        super().__init__(f"Emoji {emoji} validation error.")


def emoji_validator(emoji: str) -> str:
    # Регулярное выражение для проверки emoji
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f700-\U0001f77f"  # alchemical symbols
        "\U0001f780-\U0001f7ff"  # Geometric Shapes Extended
        "\U0001f800-\U0001f8ff"  # Supplemental Arrows-C
        "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
        "\U0001fa00-\U0001fa6f"  # Chess Symbols
        "\U00002702-\U000027b0"  # Dingbats
        "]+",
        flags=re.UNICODE,
    )

    if not emoji_pattern.fullmatch(emoji):
        raise EmojiValidationError(emoji)
    return emoji
