"""
Centralized configuration for model training and inference.
Edit this file to change model paths, hyperparameters, and data locations.
"""
import os

# Model paths
INTENT_MODEL_PATH = os.getenv("INTENT_MODEL_PATH", "intent_model_enhanced")
NER_MODEL_PATH = os.getenv("NER_MODEL_PATH", "slot_ner_model")

# Data paths
INTENT_DATA_PATH = os.getenv("INTENT_DATA_PATH", "../data/intent_slot_dataset.jsonl")
NER_DATA_PATH = os.getenv("NER_DATA_PATH", "../data/slot_ner_dataset_merged.jsonl")

# Training hyperparameters
MAX_LENGTH = 128
BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 2e-5

# Device selection
import torch
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
