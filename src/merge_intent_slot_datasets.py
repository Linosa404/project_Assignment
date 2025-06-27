import json
import os

# Paths to the two merged files (update if needed)
MERGED1 = "data/intent_slot_dataset_merged_augmented.jsonl"
MERGED2 = "data/intent_slot_dataset.jsonl"
OUTPUT = "data/intent_slot_dataset_merged_final.jsonl"

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
    data1 = load_jsonl(MERGED1)
    data2 = load_jsonl(MERGED2)
    all_data = data1 + data2
    merged = deduplicate(all_data)
    save_jsonl(OUTPUT, merged)
    print(f"Final merged dataset saved to {OUTPUT} with {len(merged)} examples.")

if __name__ == "__main__":
    main()
