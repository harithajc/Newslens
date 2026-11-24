"""Export unique stories into a sheet for team labeling."""

import csv
from pathlib import Path

from APP.backend.database import get_stories


OUTPUT_PATH = Path(__file__).resolve().parent / "labeling_sheet.csv"


def main() -> None:
    stories = get_stories(limit=10000)
    seen_titles = set()
    rows = []

    for story in stories:
        title = story.get("title", "").strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        rows.append(
            {
                "id": story.get("id", ""),
                "title": title,
                "summary": story.get("summary", "").strip(),
                "label_person1": "",
                "label_person2": "",
            }
        )

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=["id", "title", "summary", "label_person1", "label_person2"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
