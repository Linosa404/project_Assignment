#!/usr/bin/env python3
"""
Unified inference script for intent and slot NER models.
Usage:
    python infer.py --task intent --text "Your query here"
    python infer.py --task ner --text "Your query here"
"""
import argparse
import logging
from config import *

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def infer_intent(text):
    from infer_intent_slot import predict_intent
    logger.info(f"Predicting intent for: {text}")
    return predict_intent(text)

def infer_ner(text):
    from infer_slot_ner import extract_slots
    logger.info(f"Extracting slots for: {text}")
    return extract_slots(text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified inference script.")
    parser.add_argument('--task', choices=['intent', 'ner'], required=True, help='Task to infer: intent or ner')
    parser.add_argument('--text', type=str, required=True, help='Input text for inference')
    args = parser.parse_args()

    if args.task == 'intent':
        result = infer_intent(args.text)
        print(f"Intent: {result}")
    elif args.task == 'ner':
        result = infer_ner(args.text)
        print(f"Slots: {result}")
