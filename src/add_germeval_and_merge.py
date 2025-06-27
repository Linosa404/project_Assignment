"""
Script to download GermEval 2014 NER dataset, convert to custom slot NER format, merge with local data, and save merged dataset.
"""
import os
import json
import requests
import zipfile
import shutil

def download_and_extract_germeval(dest_dir="data/germeval2018"):
    print("Assuming GermEval 2018 files are already placed in the directory.")
    return

def parse_germeval_to_jsonl(input_path, output_path):
    """
    Converts GermEval 2014 NER .tsv file to JSONL format with 'text' and 'labels' (BIO format).
    """
    examples = []
    with open(input_path, encoding="utf-8") as f:
        tokens = []
        labels = []
        for line in f:
            line = line.strip()
            if not line:
                if tokens:
                    text = " ".join(tokens)
                    spans = []
                    current = None
                    start = 0
                    for i, (token, label) in enumerate(zip(tokens, labels)):
                        if label.startswith("B-"):
                            if current:
                                spans.append([start, start+len(current)-1, current_label])
                            current = token
                            current_label = label[2:]
                            start = text.find(token, start)
                        elif label.startswith("I-") and current:
                            current += " " + token
                        else:
                            if current:
                                spans.append([start, start+len(current)-1, current_label])
                                current = None
                    if current:
                        spans.append([start, start+len(current)-1, current_label])
                    examples.append({"text": text, "labels": spans})
                    tokens = []
                    labels = []
                continue
            parts = line.split()
            if len(parts) >= 2:
                tokens.append(parts[0])
                labels.append(parts[-1])
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Converted GermEval data to {output_path} with {len(examples)} examples.")

def merge_with_local(local_path, germeval_path, merged_path):
    with open(local_path) as f:
        local = [json.loads(line) for line in f]
    with open(germeval_path) as f:
        germeval = [json.loads(line) for line in f]
    merged = local + germeval
    with open(merged_path, "w") as f:
        for ex in merged:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Merged dataset saved as {merged_path} with {len(merged)} examples.")

def main():
    dest_dir = "data/germeval2018"
    download_and_extract_germeval(dest_dir)
    tsv_path = os.path.join(dest_dir, "NER-de-train.tsv")
    germeval_jsonl = os.path.join(dest_dir, "germeval_train.jsonl")
    parse_germeval_to_jsonl(tsv_path, germeval_jsonl)
    local_path = "data/slot_ner_dataset_merged.jsonl"
    merged_path = "data/slot_ner_dataset_merged_plus_germeval.jsonl"
    merge_with_local(local_path, germeval_jsonl, merged_path)

if __name__ == "__main__":
    main()
