import html
import re
from typing import Optional


def clean_story_text(value: Optional[str]) -> str:
    """Unescape entities, remove markup, and normalize whitespace."""
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]*>", " ", text)
    return " ".join(text.split())


def _normalized_story_text(value: Optional[str]) -> str:
    return "".join(
        character
        for character in clean_story_text(value).casefold()
        if character.isalnum()
    )


def is_comic_available(headline: Optional[str], summary: Optional[str]) -> bool:
    cleaned_summary = clean_story_text(summary)
    return (
        len(cleaned_summary) >= 40
        and _normalized_story_text(cleaned_summary)
        != _normalized_story_text(headline)
    )