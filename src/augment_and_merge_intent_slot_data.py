import json
import random
import os

MAIN_DATASET = "data/intent_slot_dataset.jsonl"
AUGMENTED_DATASET = "data/augmented_intent_slot_dataset.jsonl"
OUTPUT_DATASET = "data/intent_slot_dataset_merged_augmented.jsonl"

# Optionally, generate more synthetic queries (add here or use an external generator)
EXTRA_SYNTHETIC = [
    {"text": "Brauche einen Flug nach Madrid am Samstag", "intent": "flight", "slots": {"destination": "Madrid", "date": "Samstag"}},
    {"text": "Any 4* hotels in Rome for next Friday?", "intent": "hotel", "slots": {"city": "Rome", "stars": 4, "date": "next Friday"}},
    {"text": "Wie ist das Wetter in Zürich nächste Woche?", "intent": "weather", "slots": {"city": "Zürich", "date": "nächste Woche"}},
    {"text": "Find attractions in Munich for kids", "intent": "attraction", "slots": {"city": "Munich", "type": "kids"}},
    {"text": "flite to barcelona 2morrow", "intent": "flight", "slots": {"destination": "Barcelona", "date": "tomorrow"}},
    {"text": "Hotel Berlin 3 Nächte ab Montag", "intent": "hotel", "slots": {"city": "Berlin", "nights": 3, "start_date": "Montag"}},
    {"text": "Wetter in Wien heute?", "intent": "weather", "slots": {"city": "Wien", "date": "heute"}},
    {"text": "Museen in Paris offen am Sonntag?", "intent": "attraction", "slots": {"city": "Paris", "type": "museum", "date": "Sonntag"}},
]

def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def deduplicate(data):
    seen = set()
    result = []
    for item in data:
        key = (item["text"].strip().lower(), item.get("intent", ""))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def main():
    main_data = load_jsonl(MAIN_DATASET)
    aug_data = load_jsonl(AUGMENTED_DATASET)
    all_data = main_data + aug_data + EXTRA_SYNTHETIC
    merged = deduplicate(all_data)
    random.shuffle(merged)
    save_jsonl(OUTPUT_DATASET, merged)
    print(f"Merged dataset saved to {OUTPUT_DATASET} with {len(merged)} examples.")

if __name__ == "__main__":
    main()
