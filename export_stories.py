import csv
from APP.backend.database import get_stories

stories = get_stories(1000, None)
with open("stories.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "headline", "summary", "label", "note"])
    for s in stories:
        w.writerow([s.get("id", ""), s.get("title", ""), s.get("summary", ""), "", ""])
print(f"Wrote {len(stories)} stories to stories.csv")