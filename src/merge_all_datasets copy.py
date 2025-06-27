#!/usr/bin/env python3
"""
Comprehensive JSONL Dataset Merger
Intelligently merges all training datasets while handling different formats
"""
import json
import os
from collections import defaultdict, Counter

def read_jsonl(file_path):
    """Read JSONL file and return list of entries"""
    entries = []
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found")
        return entries
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry['source_file'] = os.path.basename(file_path)
                    entry['line_number'] = line_num
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num} in {file_path}: {e}")
                    continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return entries

def normalize_entry(entry):
    """Normalize entry format to standard schema"""
    normalized = {
        'text': '',
        'intent': None,
        'slots': {},
        'source_file': entry.get('source_file', 'unknown'),
        'line_number': entry.get('line_number', 0)
    }
    
    # Handle text field
    if 'text' in entry:
        normalized['text'] = entry['text']
    elif 'sentence' in entry:
        normalized['text'] = entry['sentence']
    
    # Handle intent field
    if 'intent' in entry:
        normalized['intent'] = entry['intent']
    elif 'label' in entry:
        normalized['intent'] = entry['label']
    
    # Handle slots field
    if 'slots' in entry:
        if isinstance(entry['slots'], dict):
            normalized['slots'] = entry['slots']
        elif isinstance(entry['slots'], list):
            # Convert list format to dict format
            slot_dict = {}
            for slot in entry['slots']:
                if isinstance(slot, dict) and 'slot' in slot and 'value' in slot:
                    slot_dict[slot['slot']] = slot['value']
            normalized['slots'] = slot_dict
    
    # Handle NER format (entities list)
    if 'entities' in entry:
        for entity in entry['entities']:
            if isinstance(entity, dict) and 'entity' in entity and 'value' in entity:
                normalized['slots'][entity['entity']] = entity['value']
    
    return normalized

def deduplicate_entries(entries):
    """Remove duplicate entries based on text similarity"""
    seen_texts = set()
    unique_entries = []
    
    for entry in entries:
        text_key = entry['text'].lower().strip()
        if text_key not in seen_texts and len(text_key) > 0:
            seen_texts.add(text_key)
            unique_entries.append(entry)
    
    return unique_entries

def merge_datasets():
    """Main function to merge all datasets"""
    
    # Define all JSONL files to merge
    jsonl_files = [
        'data/slot_ner_dataset.jsonl',
        'data/slot_ner_dataset_combined.jsonl',
        'data/slot_ner_dataset_synth.jsonl',
        'data/slot_ner_dataset_datesynth.jsonl',
        'data/slot_ner_dataset_richdate.jsonl',
        'data/slot_ner_extra_examples.jsonl',
        'data/slot_ner_extra_german.jsonl',
        'data/intent_slot_dataset.jsonl',
        'data/enhanced_intent_dataset.jsonl',
        'data/enhanced_slot_ner_dataset.jsonl',
        'data/intent_dataset_enhanced_merged.jsonl',
        'data/slot_ner_dataset_enhanced_merged.jsonl',
        'data/augmented_intent_slot_dataset.jsonl',
        'data/germeval2018/germeval_train.jsonl'
    ]
    
    all_entries = []
    file_stats = {}
    
    print("🔄 Reading all JSONL files...")
    for file_path in jsonl_files:
        print(f"  📄 Reading {file_path}")
        entries = read_jsonl(file_path)
        normalized_entries = [normalize_entry(entry) for entry in entries]
        
        # Filter out entries with empty text
        valid_entries = [e for e in normalized_entries if e['text'].strip()]
        
        file_stats[file_path] = {
            'total': len(entries),
            'valid': len(valid_entries),
            'invalid': len(entries) - len(valid_entries)
        }
        
        all_entries.extend(valid_entries)
        print(f"    ✅ {len(valid_entries)} valid entries loaded")
    
    print(f"\n📊 Total entries before deduplication: {len(all_entries)}")
    
    # Deduplicate entries
    print("🔄 Deduplicating entries...")
    unique_entries = deduplicate_entries(all_entries)
    print(f"📊 Total unique entries: {len(unique_entries)}")
    print(f"🗑️  Removed {len(all_entries) - len(unique_entries)} duplicates")
    
    # Statistics
    intent_stats = Counter()
    slot_stats = defaultdict(Counter)
    source_stats = Counter()
    
    for entry in unique_entries:
        if entry['intent']:
            intent_stats[entry['intent']] += 1
        
        for slot_key, slot_value in entry['slots'].items():
            slot_stats[slot_key][slot_value] += 1
        
        source_stats[entry['source_file']] += 1
    
    # Print statistics
    print("\n📈 Dataset Statistics:")
    print(f"  Total unique entries: {len(unique_entries)}")
    print(f"  Files processed: {len(file_stats)}")
    
    print("\n🎯 Intent Distribution:")
    for intent, count in intent_stats.most_common():
        print(f"  {intent}: {count}")
    
    print("\n🏷️  Top Slot Types:")
    for slot_type, values in list(slot_stats.items())[:10]:
        print(f"  {slot_type}: {len(values)} unique values, {sum(values.values())} total")
    
    print("\n📁 Source File Distribution:")
    for source, count in source_stats.most_common():
        print(f"  {source}: {count}")
    
    # Write merged dataset
    output_file = 'data/master_merged_dataset.jsonl'
    print(f"\n💾 Writing merged dataset to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in unique_entries:
            # Remove metadata for final output
            output_entry = {
                'text': entry['text'],
                'intent': entry['intent'],
                'slots': entry['slots']
            }
            f.write(json.dumps(output_entry, ensure_ascii=False) + '\n')
    
    print(f"✅ Merged dataset saved to {output_file}")
    
    # Create separate intent and slot NER datasets
    create_specialized_datasets(unique_entries)
    
    return unique_entries

def create_specialized_datasets(entries):
    """Create specialized datasets for intent and slot NER training"""
    
    # Intent classification dataset
    intent_entries = [e for e in entries if e['intent']]
    intent_file = 'data/master_intent_dataset.jsonl'
    
    print(f"\n🎯 Creating intent dataset: {len(intent_entries)} entries")
    with open(intent_file, 'w', encoding='utf-8') as f:
        for entry in intent_entries:
            output_entry = {
                'text': entry['text'],
                'intent': entry['intent']
            }
            f.write(json.dumps(output_entry, ensure_ascii=False) + '\n')
    
    # Slot NER dataset  
    slot_entries = [e for e in entries if e['slots']]
    slot_file = 'data/master_slot_ner_dataset.jsonl'
    
    print(f"🏷️  Creating slot NER dataset: {len(slot_entries)} entries")
    with open(slot_file, 'w', encoding='utf-8') as f:
        for entry in slot_entries:
            # Convert to NER format
            output_entry = {
                'text': entry['text'],
                'entities': [
                    {'entity': k, 'value': v} 
                    for k, v in entry['slots'].items()
                ]
            }
            f.write(json.dumps(output_entry, ensure_ascii=False) + '\n')
    
    print(f"✅ Specialized datasets created")

if __name__ == "__main__":
    print("🚀 Starting comprehensive dataset merge...")
    entries = merge_datasets()
    print("\n🎉 Dataset merge completed!")
