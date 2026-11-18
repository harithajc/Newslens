from fetch_news import fetch_headlines
from database import save_stories, get_stories

stories = fetch_headlines(10)
print("Fetched from TOI:", len(stories))

save_stories(stories)
print("In database after first save:", len(get_stories(100)))

save_stories(stories)
print("In database after second save:", len(get_stories(100)))

for s in get_stories(3):
    print("-", s["title"] if isinstance(s, dict) else s)