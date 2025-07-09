"""
Inference script for intent extraction using the trained model.
"""
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import sys
import logging
from config import LOG_LEVEL

MODEL_PATH = "intent_model"

with open(f"{MODEL_PATH}/intent2id.json") as f:
    intent2id = json.load(f)
id2intent = {v: k for k, v in intent2id.items()}

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def predict_intent(text):
    try:
        logger.info(f"Predicting intent for: {text}")
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        return id2intent[pred]
    except Exception as e:
        logger.error(f"Error during intent inference: {e}")
        raise


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "What is the weather from December 16 to 23, 2025 in London?"
    intent = predict_intent(text)
    print(f"Intent: {intent}")
