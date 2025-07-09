#!/usr/bin/env python3
"""
Enhanced Intent Classification Training Script
Optimized for 80% accuracy target
"""
import json
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding
)
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from torch.utils.data import Dataset
import numpy as np
import logging
from config import DEVICE, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

class IntentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

def load_intent_data(file_path):
    """Load intent classification data"""
    texts = []
    intents = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                texts.append(data['text'])
                intents.append(data['label'])  # Changed from 'intent' to 'label'
    
    return texts, intents

def train_intent_model():
    """Train intent classification model"""
    try:
        logger.info("🎯 Training Enhanced Intent Classification Model...")
    
        # Load enhanced data
        texts, intents = load_intent_data('data/enhanced_intent_dataset.jsonl')
        logger.info(f"📊 Loaded {len(texts)} training examples")
    
        # Encode labels
        label_encoder = LabelEncoder()
        encoded_labels = label_encoder.fit_transform(intents)
    
        # Split data with better stratification
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, encoded_labels, test_size=0.15, random_state=42, stratify=encoded_labels
        )
    
        logger.info(f"🔀 Train: {len(train_texts)}, Validation: {len(val_texts)}")
        logger.info(f"📊 Intent classes: {list(label_encoder.classes_)}")
    
        # Initialize tokenizer and model
        model_name = "distilbert-base-multilingual-cased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=len(label_encoder.classes_)
        )
    
        # Create datasets
        train_dataset = IntentDataset(train_texts, train_labels, tokenizer)
        val_dataset = IntentDataset(val_texts, val_labels, tokenizer)
    
        # Optimal training arguments for 80%+ accuracy
        training_args = TrainingArguments(
            output_dir='intent_model_enhanced',
            num_train_epochs=8,  # Increased for better convergence
            per_device_train_batch_size=32,  # Larger batch size for stability
            per_device_eval_batch_size=64,   # Larger eval batch size
            warmup_steps=1000,  # More warmup steps for large dataset
            weight_decay=0.02,  # Increased weight decay for regularization
            logging_dir='./logs_intent',
            logging_steps=50,
            eval_strategy='steps',
            eval_steps=500,
            save_strategy='steps',
            save_steps=1000,
            load_best_model_at_end=True,
            metric_for_best_model='eval_accuracy',  # Changed to accuracy
            greater_is_better=True,
            save_total_limit=3,
            dataloader_pin_memory=False,
            learning_rate=3e-5,  # Slightly higher learning rate
            lr_scheduler_type='cosine',  # Cosine learning rate schedule
            gradient_accumulation_steps=2,  # Gradient accumulation for effective larger batch
            fp16=False,  # Disabled for MPS compatibility
            dataloader_num_workers=0,  # Disabled for MPS compatibility
            seed=42,
            report_to="none",  # Disable wandb logging
            remove_unused_columns=True,
            group_by_length=True,  # Group similar length sequences for efficiency
        )
    
        # Add custom metrics computation
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            accuracy = accuracy_score(labels, predictions)
            return {'accuracy': accuracy}
    
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=tokenizer,
            data_collator=DataCollatorWithPadding(tokenizer),
            compute_metrics=compute_metrics,
        )
    
        # Train model
        logger.info("🚀 Starting training...")
        trainer.train()
    
        # Save model
        model.save_pretrained('intent_model_enhanced')
        tokenizer.save_pretrained('intent_model_enhanced')
    
        # Save label encoder
        import pickle
        with open('intent_model_enhanced/label_encoder.pkl', 'wb') as f:
            pickle.dump(label_encoder, f)
    
        # Save intent to id mapping
        intent2id = {intent: idx for idx, intent in enumerate(label_encoder.classes_)}
        with open('intent_model_enhanced/intent2id.json', 'w') as f:
            json.dump(intent2id, f, indent=2)
    
        # Evaluate
        logger.info("\n🧪 Running final evaluation...")
        predictions = trainer.predict(val_dataset)
        pred_labels = np.argmax(predictions.predictions, axis=1)
    
        accuracy = accuracy_score(val_labels, pred_labels)
        logger.info(f"\n✅ Training completed!")
        logger.info(f"📊 Final Validation Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
        # Check if we met the 80% target
        if accuracy >= 0.80:
            logger.info("🎉 SUCCESS: Achieved 80%+ accuracy target!")
        else:
            logger.warning(f"⚠️ TARGET MISSED: Need {0.80-accuracy:.3f} more accuracy to reach 80%")
    
        # Detailed classification report
        intent_names = label_encoder.classes_
        logger.info(f"\n📈 Detailed Classification Report:")
        logger.info(classification_report(val_labels, pred_labels, target_names=intent_names))
    
        return model, tokenizer, label_encoder
    except Exception as e:
        logger.error(f"Error during intent model training: {e}")
        raise

if __name__ == "__main__":
    train_intent_model()
