#!/usr/bin/env python3
"""
Merge enhanced training data with existing datasets for retraining
"""

import json
import os

def merge_slot_ner_data():
    """Merge enhanced slot NER data with existing data"""
    
    existing_files = [
        "data/slot_ner_dataset_combined.jsonl",
        "data/slot_ner_dataset_merged.jsonl", 
        "data/enhanced_slot_ner_dataset.jsonl"
    ]
    
    all_data = []
    seen_texts = set()
    
    for file_path in existing_files:
        if os.path.exists(file_path):
            print(f"Loading {file_path}...")
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        item = json.loads(line.strip())
                        text = item.get('text', '').strip().lower()
                        
                        # Avoid duplicates
                        if text and text not in seen_texts:
                            all_data.append(item)
                            seen_texts.add(text)
                    except json.JSONDecodeError:
                        continue
    
    # Save merged data
    output_file = "data/slot_ner_dataset_enhanced_merged.jsonl"
    with open(output_file, 'w') as f:
        for item in all_data:
            f.write(json.dumps(item) + "\n")
    
    print(f"Merged {len(all_data)} unique slot NER examples to {output_file}")
    return output_file

def merge_intent_data():
    """Merge enhanced intent data with existing data"""
    
    existing_files = [
        "data/intent_slot_dataset.jsonl",
        "data/enhanced_intent_dataset.jsonl"
    ]
    
    all_data = []
    seen_texts = set()
    
    for file_path in existing_files:
        if os.path.exists(file_path):
            print(f"Loading {file_path}...")
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        item = json.loads(line.strip())
                        text = item.get('text', '').strip().lower()
                        
                        # Avoid duplicates
                        if text and text not in seen_texts:
                            all_data.append(item)
                            seen_texts.add(text)
                    except json.JSONDecodeError:
                        continue
    
    # Save merged data
    output_file = "data/intent_dataset_enhanced_merged.jsonl"
    with open(output_file, 'w') as f:
        for item in all_data:
            f.write(json.dumps(item) + "\n")
    
    print(f"Merged {len(all_data)} unique intent examples to {output_file}")
    return output_file

def main():
    print("Merging enhanced training data with existing datasets...")
    
    slot_file = merge_slot_ner_data()
    intent_file = merge_intent_data()
    
    print(f"\nReady for retraining:")
    print(f"- Slot NER: {slot_file}")
    print(f"- Intent: {intent_file}")
    
    print(f"\nNext steps:")
    print(f"1. python3 src/train_slot_ner_model.py --data {slot_file}")
    print(f"2. python3 src/train_intent_slot_model.py --data {intent_file}")

if __name__ == "__main__":
    main()
