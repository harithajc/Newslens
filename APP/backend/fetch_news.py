import hashlib
import feedparser

FEED_URL = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"

def fetch_headlines(limit=10):
    feed = feedparser.parse(FEED_URL)
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
        })
    return stories