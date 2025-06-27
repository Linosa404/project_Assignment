"""
Generate synthetic slot NER data for travel questions.
This script creates diverse questions and slot annotations for training.
"""
import random
import json

cities = ["Berlin", "London", "Paris", "Rome", "Madrid", "Tokyo", "New York", "Dubai", "Sydney", "Cairo"]
intents = [
    ("weather", ["What is the weather in {city} on {date}?", "Weather forecast for {city} from {start_date} to {end_date}", "How's the weather in {city} next week?"]),
    ("flight_price", ["How much does a flight from {origin} to {destination} cost on {date}?", "Find me the cheapest flight from {origin} to {destination} on {date}", "How much is a round trip flight from {origin} to {destination} leaving {start_date} and returning {end_date}?"]),
    ("hotel_search", ["Show me hotels in {city} for {start_date} to {end_date}", "What are the best hotels in {city} for {month}?", "Find hotels in {city} for {event}"]),
    ("restrictions", ["Are there any travel restrictions in {city} in {month}?", "Can I travel to {country} in {month}?", "Is it safe to travel to {country} in {month}?"])
]
dates = ["2025-07-01", "2025-12-23", "2025-03-15", "2025-04-10", "2025-06-20"]
months = ["2025-07", "2025-12", "2025-03", "2025-04", "2025-06"]
events = ["Expo 2025", "Olympics 2024", "Easter 2025"]

examples = []
for intent, templates in intents:
    for template in templates:
        for _ in range(10):
            city = random.choice(cities)
            origin = random.choice(cities)
            destination = random.choice([c for c in cities if c != origin])
            date = random.choice(dates)
            start_date = random.choice(dates)
            end_date = random.choice(dates)
            month = random.choice(months)
            event = random.choice(events)
            country = random.choice(["Japan", "Egypt", "USA", "France", "Germany"])
            text = template.format(city=city, origin=origin, destination=destination, date=date, start_date=start_date, end_date=end_date, month=month, event=event, country=country)
            # Simple slot annotation (character-based)
            labels = []
            if "{city}" in template:
                idx = text.find(city)
                labels.append([idx, idx+len(city), "city"])
            if "{origin}" in template:
                idx = text.find(origin)
                labels.append([idx, idx+len(origin), "origin"])
            if "{destination}" in template:
                idx = text.find(destination)
                labels.append([idx, idx+len(destination), "destination"])
            if "{date}" in template:
                idx = text.find(date)
                labels.append([idx, idx+len(date), "date"])
            if "{start_date}" in template:
                idx = text.find(start_date)
                labels.append([idx, idx+len(start_date), "start_date"])
            if "{end_date}" in template:
                idx = text.find(end_date)
                labels.append([idx, idx+len(end_date), "end_date"])
            if "{month}" in template:
                idx = text.find(month)
                labels.append([idx, idx+len(month), "month"])
            if "{event}" in template:
                idx = text.find(event)
                labels.append([idx, idx+len(event), "event"])
            if "{country}" in template:
                idx = text.find(country)
                labels.append([idx, idx+len(country), "country"])
            examples.append({"text": text, "labels": labels})

with open("data/slot_ner_dataset_synth.jsonl", "w") as f:
    for ex in examples:
        f.write(json.dumps(ex) + "\n")
print(f"Generated {len(examples)} synthetic NER examples.")
