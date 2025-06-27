import json
import os

# List all merged and augmented files to combine
MERGE_FILES = [
    "data/intent_slot_dataset_merged_final.jsonl",
    "data/slot_ner_dataset_merged.jsonl",
    "data/slot_ner_dataset_merged_plus_germeval.jsonl",
    "data/slot_ner_dataset_merged_backup_before_german.jsonl",
    "data/augmented_intent_slot_dataset.jsonl",
    "data/augmented_ner_german.jsonl"
]
OUTPUT = "data/all_merged_datasets.jsonl"

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
        key = (item.get("text", "").strip().lower(), item.get("intent", ""))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def main():
    all_data = []
    for path in MERGE_FILES:
        all_data.extend(load_jsonl(path))
    merged = deduplicate(all_data)
    save_jsonl(OUTPUT, merged)
    print(f"All merged datasets saved to {OUTPUT} with {len(merged)} examples.")
    # Optionally, delete the old files
    for path in MERGE_FILES:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted {path}")

if __name__ == "__main__":
    main()
