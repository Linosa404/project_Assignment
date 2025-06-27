"""
Generate even more synthetic slot NER data with a wide variety of date formats, including full ISO date strings as slot values.
"""
import random
import json
from datetime import datetime, timedelta

cities = ["Berlin", "London", "Paris", "Rome", "Madrid", "Tokyo", "New York", "Dubai", "Sydney", "Cairo"]
date_formats = [
    ("{iso}", "{iso}"),
    ("{day}.{month}.{year}", "{iso}"),
    ("{month}/{day}/{year}", "{iso}"),
    ("{day} {month_name} {year}", "{iso}"),
    ("{month_name} {day}, {year}", "{iso}"),
    ("{day} {month_name}", "{iso}"),
    ("{month_name} {day}", "{iso}"),
    ("{day}", "{iso}"),
    ("{day}th of {month_name}, {year}", "{iso}"),
    ("{day}st {month_name} {year}", "{iso}"),
    ("{day}nd {month_name} {year}", "{iso}"),
    ("{day}rd {month_name} {year}", "{iso}")
]

examples = []
for _ in range(200):
    city1 = random.choice(cities)
    city2 = random.choice([c for c in cities if c != city1])
    base_date = datetime(2024, random.randint(1, 12), random.randint(1, 25))
    start_date = base_date
    end_date = base_date + timedelta(days=random.randint(1, 7))
    for fmt, iso_fmt in date_formats:
        # Single date
        date_str = fmt.format(
            day=start_date.day,
            month=str(start_date.month).zfill(2),
            year=start_date.year,
            month_name=start_date.strftime('%B'),
            iso=start_date.strftime('%Y-%m-%d')
        )
        text = f"How much does a flight from {city1} to {city2} cost on {date_str}?"
        labels = []
        idx1 = text.find(city1)
        if idx1 != -1:
            labels.append([idx1, idx1+len(city1), "origin"])
        idx2 = text.find(city2)
        if idx2 != -1:
            labels.append([idx2, idx2+len(city2), "destination"])
        idx_date = text.find(date_str)
        if idx_date != -1:
            labels.append([idx_date, idx_date+len(date_str), "date"])
        examples.append({"text": text, "labels": labels})
        # Date range
        end_str = fmt.format(
            day=end_date.day,
            month=str(end_date.month).zfill(2),
            year=end_date.year,
            month_name=end_date.strftime('%B'),
            iso=end_date.strftime('%Y-%m-%d')
        )
        text_range = f"How much does a flight from {city1} to {city2} cost from {date_str} to {end_str}?"
        idx1 = text_range.find(city1)
        idx2 = text_range.find(city2)
        idx_start = text_range.find(date_str)
        idx_end = text_range.find(end_str)
        labels_range = []
        if idx1 != -1:
            labels_range.append([idx1, idx1+len(city1), "origin"])
        if idx2 != -1:
            labels_range.append([idx2, idx2+len(city2), "destination"])
        if idx_start != -1:
            labels_range.append([idx_start, idx_start+len(date_str), "start_date"])
        if idx_end != -1:
            labels_range.append([idx_end, idx_end+len(end_str), "end_date"])
        examples.append({"text": text_range, "labels": labels_range})

with open("data/slot_ner_dataset_richdate.jsonl", "w") as f:
    for ex in examples:
        f.write(json.dumps(ex) + "\n")
print(f"Generated {len(examples)} rich date NER examples.")
