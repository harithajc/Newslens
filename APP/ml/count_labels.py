"""Count completed labels in a labeling CSV."""

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Count labels in a labeling CSV")
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()

    if not args.csv_path.exists():
        parser.error(f"CSV not found: {args.csv_path}")

    with args.csv_path.open("r", encoding="utf-8-sig", newline="") as input_file:
        rows = list(csv.DictReader(input_file))

    person1 = 0
    person2 = 0
    both = 0
    values = []

    for row in rows:
        label1 = (row.get("label_person1") or "").strip()
        label2 = (row.get("label_person2") or "").strip()
        person1 += bool(label1)
        person2 += bool(label2)
        both += bool(label1 and label2)
        if label1:
            values.append(label1)
        if label2:
            values.append(label2)

    count_ones = sum(value == "1" for value in values)
    count_zeros = sum(value == "0" for value in values)
    total = len(values)
    percent_ones = (count_ones / total * 100) if total else 0
    percent_zeros = (count_zeros / total * 100) if total else 0

    print(f"Rows: {len(rows)}")
    print(f"label_person1: {person1}")
    print(f"label_person2: {person2}")
    print(f"Both: {both}")
    print(f"1s: {percent_ones:.1f}%")
    print(f"0s: {percent_zeros:.1f}%")


if __name__ == "__main__":
    main()
