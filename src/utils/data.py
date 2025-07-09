"""
utils/data.py
Utility functions for loading and saving datasets.
"""
import json
from typing import List, Dict, Any

def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load a JSONL file into a list of dicts."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(data: List[Dict[str, Any]], file_path: str):
    """Save a list of dicts to a JSONL file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
