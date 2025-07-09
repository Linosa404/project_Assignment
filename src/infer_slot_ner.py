"""
Inference script for slot extraction using the trained NER model.
"""
import json
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import sys
import os
import logging
from config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

MODEL_PATH = "slot_ner_model"

label2id_path = f"{MODEL_PATH}/label2id.json"
if not os.path.exists(label2id_path):
    # fallback to original model dir if not found in checkpoint
    label2id_path = "slot_ner_model/label2id.json"
with open(label2id_path) as f:
    label2id = json.load(f)
id2label = {int(v): k for k, v in label2id.items()}

def get_model_or_tokenizer_path(filename):
    checkpoint_path = os.path.join(MODEL_PATH, filename)
    fallback_path = os.path.join("slot_ner_model", filename)
    return checkpoint_path if os.path.exists(checkpoint_path) else fallback_path

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH if os.path.exists(os.path.join(MODEL_PATH, "tokenizer.json")) else "slot_ner_model")
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH if os.path.exists(os.path.join(MODEL_PATH, "config.json")) else "slot_ner_model")


def extract_slots(text):
    try:
        logger.info(f"Extracting slots for: {text}")
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs).logits
            preds = torch.argmax(outputs, dim=2)[0].tolist()
        tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        slots = {}
        current_slot = None
        current_value = []
        for token, pred in zip(tokens, preds):
            label = id2label.get(pred, "O")
            if label.startswith("B-"):
                if current_slot:
                    slots[current_slot] = tokenizer.convert_tokens_to_string(current_value).replace(' ##', '')
                current_slot = label[2:]
                current_value = [token]
            elif label.startswith("I-") and current_slot:
                current_value.append(token)
            else:
                if current_slot:
                    slots[current_slot] = tokenizer.convert_tokens_to_string(current_value).replace(' ##', '')
                    current_slot = None
                    current_value = []
        if current_slot and current_value:
            slots[current_slot] = tokenizer.convert_tokens_to_string(current_value).replace(' ##', '')
        return slots
    except Exception as e:
        logger.error(f"Error during slot NER inference: {e}")
        raise

def debug_batch_predictions(dataset_path, n=5):
    with open(dataset_path) as f:
        data = [json.loads(line) for line in f]
    for example in data[:n]:
        text = example['text']
        print("Text:", text)
        print("True labels:", example['labels'])
        print("Predicted slots:", extract_slots(text))
        print("---")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--debug-batch":
        debug_batch_predictions(sys.argv[2], n=5)
        sys.exit(0)
    text = sys.argv[1] if len(sys.argv) > 1 else "What is the weather from December 16 to 23, 2025 in London?"
    slots = extract_slots(text)
    print(f"Slots: {slots}")
