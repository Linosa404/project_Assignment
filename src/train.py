#!/usr/bin/env python3
"""
Unified training script for intent classification and slot NER.
Usage:
    python train.py --task intent
    python train.py --task ner
"""
import argparse
import logging
from config import *

# Set up logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def train_intent():
    from train_enhanced_intent_model import train_intent_model
    logger.info("Starting intent model training...")
    train_intent_model()
    logger.info("Intent model training complete.")

def train_ner():
    from ultimate_ner_trainer import UltimateSlotNERTrainer
    logger.info("Starting NER model training...")
    trainer = UltimateSlotNERTrainer(model_name=NER_MODEL_PATH)
    trainer.train()
    logger.info("NER model training complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified training script.")
    parser.add_argument('--task', choices=['intent', 'ner'], required=True, help='Task to train: intent or ner')
    args = parser.parse_args()

    if args.task == 'intent':
        train_intent()
    elif args.task == 'ner':
        train_ner()
