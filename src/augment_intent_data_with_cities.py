"""
Script to generate additional intent/slot training data for all world cities.
- Uses a world cities CSV (e.g., simplemaps.com/data/world-cities or geonames.org)
- Produces synthetic queries for flights, hotels, and weather.
- Appends to your existing intent_slot_dataset.jsonl
"""
import csv
import json
import random
from datetime import datetime, timedelta

CITIES_CSV = "data/worldcities.csv"  # Download from simplemaps.com/data/world-cities or similar
OUTPUT_JSONL = "data/intent_slot_dataset.jsonl"

# Example templates
TEMPLATES = [
    ("flight_price", "How much does a flight from {origin} to {destination} cost from {start_date} to {end_date}?"),
    ("flight_search", "Show me flights from {origin} to {destination} from {start_date} to {end_date}"),
    ("hotel_search", "Show me hotels in {city} for {start_date} to {end_date}"),
    ("weather", "What is the weather in {city} from {start_date} to {end_date}?")
]

# Load cities
with open(CITIES_CSV) as f:
    reader = csv.DictReader(f)
    cities = [row['city'] for row in reader if row.get('city')]

# Generate random date ranges
this_year = datetime.now().year

def random_date_range():
    start = datetime(this_year, random.randint(1, 12), random.randint(1, 25))
    end = start + timedelta(days=random.randint(2, 7))
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

# Generate examples
examples = []
for _ in range(20000):  # Generate 20k examples
    template = random.choice(TEMPLATES)
    intent, text_template = template
    if intent.startswith("flight"):
        origin, destination = random.sample(cities, 2)
        start_date, end_date = random_date_range()
        text = text_template.format(origin=origin, destination=destination, start_date=start_date, end_date=end_date)
        slots = {"origin": origin, "destination": destination, "start_date": start_date, "end_date": end_date}
    else:
        city = random.choice(cities)
        start_date, end_date = random_date_range()
        text = text_template.format(city=city, start_date=start_date, end_date=end_date)
        slots = {"city": city, "start_date": start_date, "end_date": end_date}
    examples.append({"text": text, "intent": intent, "slots": slots})

# Append to existing dataset
with open(OUTPUT_JSONL, "a") as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print(f"Added {len(examples)} new examples to {OUTPUT_JSONL}")
