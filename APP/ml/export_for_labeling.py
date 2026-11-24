"""Export a shuffled batch of unique stories for team labeling."""

import argparse
import csv
import random
from pathlib import Path

from APP.backend.database import get_stories


ML_DIR = Path(__file__).resolve().parent
FIELD_NAMES = [
    "id",
    "title",
    "summary",
    "section",
    "label_person1",
    "label_person2",
]


def next_output_path() -> Path:
    number = 1
    while True:
        path = ML_DIR / f"labeling_batch_{number}.csv"
        if not path.exists():
            return path
        number += 1


def load_excluded_ids(paths: list[str]) -> set[str]:
    excluded = set()
    for path_text in paths:
        path = Path(path_text)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as input_file:
            reader = csv.DictReader(input_file)
            for row in reader:
                story_id = (row.get("id") or "").strip()
                if story_id:
                    excluded.add(story_id)
    return excluded


def main() -> None:
    parser = argparse.ArgumentParser(description="Export stories for labeling")
    parser.add_argument("--exclude", nargs="+", default=[], help="CSV files whose IDs are already used")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    output_path = args.out.resolve() if args.out else next_output_path()
    if args.out and not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()
    if output_path.exists():
        parser.error(f"Output already exists: {output_path}")

    excluded = load_excluded_ids(args.exclude)
    stories = get_stories(limit=max(args.limit * 20, 1000))
    seen_titles = set()
    rows = []
    skipped = 0

    for story in stories:
        story_id = story.get("id", "").strip()
        title = story.get("title", "").strip()
        if not story_id or not title:
            skipped += 1
            continue
        if story_id in excluded or title in seen_titles:
            skipped += 1
            continue
        seen_titles.add(title)
        rows.append(
            {
                "id": story_id,
                "title": title,
                "summary": story.get("summary", "").strip(),
                "section": story.get("section", "").strip() or "Top",
                "label_person1": "",
                "label_person2": "",
            }
        )
        if len(rows) == args.limit:
            break

    random.Random(42).shuffle(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELD_NAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_path}")
    print(f"Skipped {skipped} rows")


if __name__ == "__main__":
    main()
