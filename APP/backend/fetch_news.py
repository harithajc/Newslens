import hashlib
import feedparser

if __package__:
    from .story_text import clean_story_text
else:
    from story_text import clean_story_text

FEEDS = {
    "Top": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Most recent": "https://timesofindia.indiatimes.com/rssfeedmostrecent.cms",
    "India": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "World": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "Business": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
    "Sports": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
}


def _story_from_entry(entry, feed_name):
    link = entry.get("link", "")
    return {
        "id": hashlib.md5(link.encode()).hexdigest()[:10],
        "title": clean_story_text(entry.get("title", "")),
        "summary": clean_story_text(entry.get("summary", "")),
        "link": link,
        "source": "Times of India",
        "published": entry.get("published", ""),
        "section": feed_name,
    }


def fetch_headlines(limit=10, feed_name="Top"):
    feed = feedparser.parse(FEEDS[feed_name])
    return [
        _story_from_entry(entry, feed_name)
        for entry in feed.entries[:limit]
    ]


def fetch_all_feeds(limit=10):
    """Fetch every configured feed and skip feeds that fail."""
    combined = []
    seen_links = set()
    for feed_name in FEEDS:
        try:
            feed = feedparser.parse(FEEDS[feed_name])
            if getattr(feed, "bozo", False):
                print(
                    f"Warning: {feed_name}: 0 stories (fetch failed); skipping.",
                    flush=True,
                )
                continue
            entries = getattr(feed, "entries", [])
            if not entries:
                print(
                    f"Warning: {feed_name}: 0 stories (no entries); skipping.",
                    flush=True,
                )
                continue

            story_count = len(entries)
            story_label = "story" if story_count == 1 else "stories"
            print(f"{feed_name}: {story_count} {story_label}", flush=True)
            for entry in entries[:limit]:
                story = _story_from_entry(entry, feed_name)
                link = story["link"]
                if link and link in seen_links:
                    continue
                if link:
                    seen_links.add(link)
                combined.append(story)
        except Exception as exc:
            print(
                f"Warning: {feed_name}: 0 stories "
                f"({type(exc).__name__}); skipping.",
                flush=True,
            )
    return combined