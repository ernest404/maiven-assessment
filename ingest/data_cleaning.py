"""Text cleaning for regulatory documents."""

import re
from html import unescape

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(value: str | None) -> str | None:
    """Strip HTML tags, unescape entities, normalise whitespace."""
    if value is None:
        return None
    text = unescape(value)
    text = TAG_RE.sub("", text)
    text = text.replace("\xa0", " ")
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text or None
