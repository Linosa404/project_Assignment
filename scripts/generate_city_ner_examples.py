import csv
import json

# Read all cities from the CSV
cities = []
with open('../data/worldcities.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cities.append(row['city'])

examples = []
# Example templates
flight_template = "I want to fly from {origin} to {destination} on March 15th"
hotel_template = "Book me a hotel in {city} from 20-25 December"
weather_template = "Wie ist das Wetter in {city} am 10. August?"

for i, city in enumerate(cities):
    # Use next city as destination for flight example
    origin = city
    destination = cities[(i+1)%len(cities)]
    # Flight example
    text = flight_template.format(origin=origin, destination=destination)
    tokens = text.split()
    labels = ["O"] * len(tokens)
    for idx, token in enumerate(tokens):
        if token == origin:
            labels[idx] = "B-origin"
        elif token == destination:
            labels[idx] = "B-destination"
        elif token == "March":
            labels[idx] = "B-date"
        elif token == "15th":
            labels[idx] = "I-date"
    examples.append({"text": text, "tokens": tokens, "labels": labels})
    # Hotel example
    text = hotel_template.format(city=city)
    tokens = text.split()
    labels = ["O"] * len(tokens)
    for idx, token in enumerate(tokens):
        if token == city:
            labels[idx] = "B-city"
        elif token == "20-25":
            labels[idx] = "B-date_range"
        elif token == "December":
            labels[idx] = "I-date_range"
    examples.append({"text": text, "tokens": tokens, "labels": labels})
    # Weather example
    text = weather_template.format(city=city)
    tokens = text.split()
    labels = ["O"] * len(tokens)
    for idx, token in enumerate(tokens):
        if token == city:
            labels[idx] = "B-city"
        elif token == "10.":
            labels[idx] = "B-date"
        elif token == "August?":
            labels[idx] = "I-date"
    examples.append({"text": text, "tokens": tokens, "labels": labels})

# Write to JSONL
with open('../data/city_ner_examples.jsonl', 'w', encoding='utf-8') as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + '\n')

print(f"Wrote {len(examples)} NER examples to ../data/city_ner_examples.jsonl")
