"""
Generate synthetic slot NER data focused on date range expressions for travel questions.
"""
import random
import json

cities = ["Berlin", "London", "Paris", "Rome", "Madrid", "Tokyo", "New York", "Dubai", "Sydney", "Cairo"]
date_formats = [
    ("from {start} to {end}, {year}", "{start_full}", "{end_full}"),
    ("from {start}.{month}.{year} to {end}.{month}.{year}", "{start_full}", "{end_full}"),
    ("from {start} {month_name} to {end} {month_name} {year}", "{start_full}", "{end_full}"),
    ("from {start} to {end} {month_name} {year}", "{start_full}", "{end_full}"),
    ("from {start}/{month}/{year} to {end}/{month}/{year}", "{start_full}", "{end_full}"),
    ("from {start} {month_name} {year} to {end} {month_name} {year}", "{start_full}", "{end_full}"),
    # New formats:
    ("from {start_full} to {end_full}", "{start_full}", "{end_full}"),  # ISO
    ("from {start_slash} to {end_slash}", "{start_slash}", "{end_slash}"),
    ("from {start_dash} to {end_dash}", "{start_dash}", "{end_dash}"),
    ("from {start_ordinal} to {end_ordinal} {month_name} {year}", "{start_ordinal_full}", "{end_ordinal_full}"),
    ("from next Friday to next Sunday", "next Friday", "next Sunday"),
    ("from tomorrow to next week", "tomorrow", "next week"),
    ("from in 2 weeks to in 3 weeks", "in 2 weeks", "in 3 weeks"),
    ("vom {start}. {month}. {year} bis {end}. {month}. {year}", "{start_german}", "{end_german}"),
    ("vom {start}. {month_name} {year} bis {end}. {month_name} {year}", "{start_german_name}", "{end_german_name}"),
]

examples = []
for _ in range(100):
    city1 = random.choice(cities)
    city2 = random.choice([c for c in cities if c != city1])
    year = random.choice(["2024", "2025", "2026"])
    month = random.choice(["12", "07", "03", "04", "06"])
    month_name = random.choice(["December", "July", "March", "April", "June"])
    start = random.choice(["23", "1", "15", "10", "28"])
    end = str(int(start) + random.randint(1, 7))
    start_full = f"{year}-{month}-{start.zfill(2)}"
    end_full = f"{year}-{month}-{end.zfill(2)}"
    start_slash = f"{month}/{start}/{year}"
    end_slash = f"{month}/{end}/{year}"
    start_dash = f"{start}-{month}-{year}"
    end_dash = f"{end}-{month}-{year}"
    start_ordinal = f"{int(start)}th"
    end_ordinal = f"{int(end)}th"
    start_ordinal_full = f"{int(start)}th {month_name} {year}"
    end_ordinal_full = f"{int(end)}th {month_name} {year}"
    start_german = f"{start}.{month}.{year}"
    end_german = f"{end}.{month}.{year}"
    start_german_name = f"{start}. {month_name} {year}"
    end_german_name = f"{end}. {month_name} {year}"
    for fmt, s_full, e_full in date_formats:
        text = f"How much does a flight from {city1} to {city2} cost {fmt.format(start=start, end=end, year=year, month=month, month_name=month_name, start_full=start_full, end_full=end_full, start_slash=start_slash, end_slash=end_slash, start_dash=start_dash, end_dash=end_dash, start_ordinal=start_ordinal, end_ordinal=end_ordinal, start_ordinal_full=start_ordinal_full, end_ordinal_full=end_ordinal_full, start_german=start_german, end_german=end_german, start_german_name=start_german_name, end_german_name=end_german_name)}?"
        # Find slot positions
        labels = []
        idx1 = text.find(city1)
        if idx1 != -1:
            labels.append([idx1, idx1+len(city1), "origin"])
        idx2 = text.find(city2)
        if idx2 != -1:
            labels.append([idx2, idx2+len(city2), "destination"])
        # For start and end dates, try to find the slot in the text
        start_val = fmt.format(start=start, end=end, year=year, month=month, month_name=month_name, start_full=start_full, end_full=end_full, start_slash=start_slash, end_slash=end_slash, start_dash=start_dash, end_dash=end_dash, start_ordinal=start_ordinal, end_ordinal=end_ordinal, start_ordinal_full=start_ordinal_full, end_ordinal_full=end_ordinal_full).split(' to ')[0].strip()
        end_val = fmt.format(start=start, end=end, year=year, month=month, month_name=month_name, start_full=start_full, end_full=end_full, start_slash=start_slash, end_slash=end_slash, start_dash=start_dash, end_dash=end_dash, start_ordinal=start_ordinal, end_ordinal=end_ordinal, start_ordinal_full=start_ordinal_full, end_ordinal_full=end_ordinal_full).split(' to ')[-1].strip()
        idx_start = text.find(start_val)
        idx_end = text.find(end_val)
        if idx_start != -1:
            labels.append([idx_start, idx_start+len(start_val), "start_date"])
        if idx_end != -1:
            labels.append([idx_end, idx_end+len(end_val), "end_date"])
        examples.append({"text": text, "labels": labels})

with open("data/slot_ner_dataset_datesynth.jsonl", "w") as f:
    for ex in examples:
        f.write(json.dumps(ex) + "\n")
print(f"Generated {len(examples)} synthetic date-focused NER examples.")