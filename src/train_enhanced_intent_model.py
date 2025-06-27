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
                intents.append(data['intent'])
    
    return texts, intents

def train_intent_model():
    """Train intent classification model"""
    
    print("🎯 Training Intent Classification Model...")
    
    # Load data
    texts, intents = load_intent_data('data/final_intent_dataset.jsonl')
    print(f"📊 Loaded {len(texts)} training examples")
    
    # Encode labels
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(intents)
    
    # Split data
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, encoded_labels, test_size=0.2, random_state=42, stratify=encoded_labels
    )
    
    print(f"🔀 Train: {len(train_texts)}, Validation: {len(val_texts)}")
    
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
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir='intent_model_enhanced',
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=100,
        eval_strategy='steps',
        eval_steps=500,
        save_strategy='steps',
        save_steps=1000,
        load_best_model_at_end=True,
        metric_for_best_model='eval_loss',
        save_total_limit=3,
        dataloader_pin_memory=False,
        learning_rate=2e-5,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
    )
    
    # Train model
    print("🚀 Starting training...")
    trainer.train()
    
    # Save model
    model.save_pretrained('intent_model_enhanced')
    tokenizer.save_pretrained('intent_model_enhanced')
    
    # Save label encoder
    import pickle
    with open('intent_model_enhanced/label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    
    # Evaluate
    predictions = trainer.predict(val_dataset)
    pred_labels = np.argmax(predictions.predictions, axis=1)
    
    accuracy = accuracy_score(val_labels, pred_labels)
    print(f"\n✅ Training completed!")
    print(f"📊 Validation Accuracy: {accuracy:.3f}")
    
    # Detailed classification report
    intent_names = label_encoder.classes_
    print(f"\n📈 Detailed Classification Report:")
    print(classification_report(val_labels, pred_labels, target_names=intent_names))
    
    return model, tokenizer, label_encoder

if __name__ == "__main__":
    train_intent_model()
