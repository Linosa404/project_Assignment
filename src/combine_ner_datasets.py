"""
Combine all slot NER datasets into one file for training.
"""
import glob
import json

output_path = "data/slot_ner_dataset_combined.jsonl"
input_paths = [
    "data/slot_ner_dataset.jsonl",
    "data/slot_ner_dataset_synth.jsonl",
    "data/slot_ner_dataset_datesynth.jsonl",
    "data/slot_ner_dataset_richdate.jsonl"
]

with open(output_path, "w") as fout:
    for path in input_paths:
        try:
            with open(path) as fin:
                for line in fin:
                    fout.write(line)
        except FileNotFoundError:
            continue
print(f"Combined datasets into {output_path}")
