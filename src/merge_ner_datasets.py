# Script to download SNIPS dataset, map slots to custom schema, and merge with local NER data
from datasets import load_dataset
import json

# 1. Download SNIPS dataset
dataset = load_dataset("snips_built_in_intents")

# 2. Map SNIPS slot labels to custom schema
def map_snips_slots_to_custom_schema(example):
    slot_map = {
        "from": "origin",
        "to": "destination",
        "departure_date": "start_date",
        "return_date": "end_date",
        "city": "city",
        "country": "country",
        "date": "date",
        # Add more mappings as needed
    }
    text = example["text"]
    labels = []
    if "slots" in example:
        for slot in example["slots"]:
            slot_name = slot["slot_name"]
            if slot_name in slot_map:
                start = slot["start"]
                end = slot["end"]
                labels.append([start, end, slot_map[slot_name]])
    return {"text": text, "labels": labels}

# 3. Convert SNIPS train split to our format
snips_examples = []
for ex in dataset["train"]:
    mapped = map_snips_slots_to_custom_schema(ex)
    if mapped["labels"]:
        snips_examples.append(mapped)

# 4. Load your own data
with open("data/slot_ner_dataset_combined.jsonl") as f:
    own_data = [json.loads(line) for line in f]

# 5. Merge and save
combined = own_data + snips_examples
with open("data/slot_ner_dataset_merged.jsonl", "w") as f:
    for ex in combined:
        f.write(json.dumps(ex) + "\n")

print(f"Merged dataset saved as data/slot_ner_dataset_merged.jsonl with {len(combined)} examples.")
