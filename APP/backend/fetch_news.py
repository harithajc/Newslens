import hashlib
import feedparser

FEEDS = {
    "Top": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Most recent": "https://timesofindia.indiatimes.com/rssfeedmostrecent.cms",
}

# India, Business, World and Sports feed URLs will be added after we verify them.


def fetch_headlines(limit=10, feed_name="Top"):
    feed = feedparser.parse(FEEDS[feed_name])
    stories = []
    for entry in feed.entries[:limit]:
        link = entry.get("link", "")
        stories.append({
            "id": hashlib.md5(link.encode()).hexdigest()[:10],
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link": link,
            "source": "Times of India",
            "published": entry.get("published", ""),
            "section": feed_name,
        })
    return stories


def fetch_all_feeds(limit=10):
    """Fetch every configured feed and skip feeds that fail."""
    combined = []
    for feed_name in FEEDS:
        try:
            feed = feedparser.parse(FEEDS[feed_name])
            if getattr(feed, "bozo", False) and not feed.entries:
                raise RuntimeError("Feed returned no usable entries")
            combined.extend(fetch_headlines(limit=limit, feed_name=feed_name))
        except Exception as exc:
            print(f"Warning: could not fetch {feed_name} feed: {exc}", flush=True)
    return combined