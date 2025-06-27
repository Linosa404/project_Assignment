import random
import json

# Example slot values for German travel NER
german_cities = ["Berlin", "München", "Hamburg", "Frankfurt", "Köln", "Stuttgart", "Düsseldorf"]
dates = ["10. Juli 2025", "20. Juli 2025", "30. Juli 2025", "15. August 2025"]
hotels = ["Hotel Adlon", "Hilton Berlin", "Maritim Hotel", "InterContinental"]
parks = ["Tiergarten", "Englischer Garten", "Central Park"]

TEMPLATES = [
    ("Buche einen Flug von {origin} nach {destination} am {date}.", [
        ("origin", "{origin}"), ("destination", "{destination}"), ("date", "{date}")]),
    ("Ich brauche ein Hotel in {city} vom {start_date} bis {end_date}.", [
        ("city", "{city}"), ("start_date", "{start_date}"), ("end_date", "{end_date}")]),
    ("Gibt es Hotels in der Nähe vom {park} in {city}?", [
        ("park", "{park}"), ("city", "{city}")]),
    ("Wie ist das Wetter in {city} am {date}?", [
        ("city", "{city}"), ("date", "{date}")]),
]

examples = []
for _ in range(100):
    template, slots = random.choice(TEMPLATES)
    values = {
        "origin": random.choice(german_cities),
        "destination": random.choice(german_cities),
        "date": random.choice(dates),
        "city": random.choice(german_cities),
        "start_date": random.choice(dates),
        "end_date": random.choice(dates),
        "hotel": random.choice(hotels),
        "park": random.choice(parks),
    }
    text = template.format(**values)
    labels = []
    for slot, slot_fmt in slots:
        slot_value = slot_fmt.format(**values)
        start = text.find(slot_value)
        if start != -1:
            end = start + len(slot_value)
            labels.append([start, end, slot])
    examples.append({"text": text, "labels": labels})

with open("data/augmented_ner_german.jsonl", "w") as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print("Generated 100 augmented German NER examples in data/augmented_ner_german.jsonl")
