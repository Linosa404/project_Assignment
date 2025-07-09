#!/usr/bin/env python3
"""
Ultimate Multilingual Slot NER Trainer
- Optimized for high F1-score (target >85%)
- Supports English/German/multilingual
- Production-ready with hardware optimization
"""

import json
import torch
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
    EarlyStoppingCallback
)
from datasets import Dataset
import evaluate
from torch.utils.data import DataLoader
import logging
from config import DEVICE, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Hardware optimization
DEVICE = torch.device("cuda" if torch.cuda.is_available() else 
                     "mps" if torch.backends.mps.is_available() else "cpu")
logger.info(f"🚀 Using device: {DEVICE}")

class HighPerfNERDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

class UltimateSlotNERTrainer:
    def __init__(self, model_name="bert-base-multilingual-cased"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.data_collator = DataCollatorForTokenClassification(self.tokenizer)
        self.metric = evaluate.load("seqeval")

    def load_and_preprocess_data(self, file_path):
        """Load and preprocess data with BIO tags"""
        with open(file_path) as f:
            data = [json.loads(line) for line in f]

        # Dynamic label mapping
        all_labels = sorted(list(set(
            label for sample in data 
            for label in sample['labels']
        )))
        self.label2id = {label: i for i, label in enumerate(all_labels)}
        self.id2label = {i: label for label, i in self.label2id.items()}

        # Tokenize and align labels
        tokenized_inputs = self.tokenizer(
            [sample['tokens'] for sample in data],
            is_split_into_words=True,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        )

        labels = []
        for i, sample in enumerate(data):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            label_ids = []
            previous_word_idx = None
            
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)
                elif word_idx != previous_word_idx:
                    label_ids.append(self.label2id[sample['labels'][word_idx]])
                else:
                    label_ids.append(-100)  # For subword tokens
                previous_word_idx = word_idx
            
            labels.append(label_ids)

        return tokenized_inputs, labels

    def compute_metrics(self, eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=2)

        true_predictions = [
            [self.id2label[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [self.id2label[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]

        results = self.metric.compute(
            predictions=true_predictions,
            references=true_labels
        )
        
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"]
        }

    def train(self, train_file, output_dir="ner_model_pro"):
        try:
            # Load data
            encodings, labels = self.load_and_preprocess_data(train_file)
            dataset = HighPerfNERDataset(encodings, labels)
            
            # Split data
            train_dataset, eval_dataset = train_test_split(
                dataset, test_size=0.15, random_state=42
            )

            # Model initialization
            model = AutoModelForTokenClassification.from_pretrained(
                self.model_name,
                num_labels=len(self.label2id),
                id2label=self.id2label,
                label2id=self.label2id,
                ignore_mismatched_sizes=True
            ).to(DEVICE)

            # Optimized training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                eval_strategy="steps",
                eval_steps=200,
                save_strategy="steps",
                save_steps=200,
                learning_rate=5e-5,
                per_device_train_batch_size=32,
                per_device_eval_batch_size=64,
                num_train_epochs=7,
                weight_decay=0.01,
                warmup_ratio=0.1,
                gradient_accumulation_steps=2,
                fp16=torch.cuda.is_available(),
                load_best_model_at_end=True,
                metric_for_best_model="f1",
                greater_is_better=True,
                logging_dir=f"{output_dir}/logs",
                report_to="none",
                optim="adamw_torch_fused",
                group_by_length=True,
                save_total_limit=2
            )

            # Trainer with early stopping
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self.tokenizer,
                data_collator=self.data_collator,
                compute_metrics=self.compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
            )

            # Train!
            logger.info("🔥 Starting high-performance training")
            trainer.train()

            # Save everything
            trainer.save_model(output_dir)
            self.tokenizer.save_pretrained(output_dir)
            with open(f"{output_dir}/label_mappings.json", "w") as f:
                json.dump({"label2id": self.label2id, "id2label": self.id2label}, f)

            # Final evaluation
            results = trainer.evaluate()
            logger.info(f"🏆 Final Metrics: {results}")

            return model, results
        except Exception as e:
            logger.error(f"Error during ultimate slot NER training: {e}")
            raise

if __name__ == "__main__":
    trainer = UltimateSlotNERTrainer(model_name="bert-base-multilingual-cased")
    model, results = trainer.train(
        train_file="data/ultimate_slot_ner_dataset.jsonl",
        output_dir="ultra_ner_model"
    )