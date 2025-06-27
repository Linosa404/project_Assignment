#!/usr/bin/env python3
"""
Enhanced Slot NER Training Script
Optimized for 80% accuracy target
"""
import json
import torch
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    TrainingArguments, Trainer, DataCollatorForTokenClassification
)
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
import numpy as np

class SlotNERDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        labels = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt',
            is_split_into_words=False
        )
        
        # Create label alignment for tokens
        aligned_labels = [-100] * self.max_length
        
        # Simple approach: assign O to all tokens, then set entity tokens
        for i in range(len(encoding['input_ids'][0])):
            if i < len(labels):
                aligned_labels[i] = labels[i]
            else:
                aligned_labels[i] = 0  # O tag
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(aligned_labels, dtype=torch.long)
        }

def create_bio_labels(text, entities, label2id):
    """Create BIO labels for NER"""
    words = text.split()
    labels = ['O'] * len(words)
    
    for entity in entities:
        entity_value = entity['value']
        entity_type = entity['entity']
        
        # Find entity in text
        for i, word in enumerate(words):
            if entity_value.lower() in ' '.join(words[i:i+len(entity_value.split())]).lower():
                if len(entity_value.split()) == 1:
                    labels[i] = f'B-{entity_type}'
                else:
                    for j in range(len(entity_value.split())):
                        if i + j < len(labels):
                            if j == 0:
                                labels[i + j] = f'B-{entity_type}'
                            else:
                                labels[i + j] = f'I-{entity_type}'
                break
    
    return [label2id.get(label, 0) for label in labels]

def load_slot_data(file_path):
    """Load slot NER data"""
    texts = []
    all_labels = []
    
    # Create label mapping
    unique_labels = set(['O'])
    
    # First pass: collect all unique labels
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                entities = data.get('entities', [])
                for entity in entities:
                    entity_type = entity['entity']
                    unique_labels.add(f'B-{entity_type}')
                    unique_labels.add(f'I-{entity_type}')
    
    label2id = {label: idx for idx, label in enumerate(sorted(unique_labels))}
    id2label = {idx: label for label, idx in label2id.items()}
    
    # Second pass: create training data
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                text = data['text']
                entities = data.get('entities', [])
                
                labels = create_bio_labels(text, entities, label2id)
                
                texts.append(text)
                all_labels.append(labels)
    
    return texts, all_labels, label2id, id2label

def train_slot_ner_model():
    """Train slot NER model"""
    
    print("🏷️  Training Slot NER Model...")
    
    # Load data
    texts, labels, label2id, id2label = load_slot_data('data/final_slot_ner_dataset.jsonl')
    print(f"📊 Loaded {len(texts)} training examples")
    print(f"🏷️  Label types: {len(label2id)}")
    
    # Split data
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    
    print(f"🔀 Train: {len(train_texts)}, Validation: {len(val_texts)}")
    
    # Initialize tokenizer and model
    model_name = "distilbert-base-multilingual-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(label2id),
        id2label=id2label,
        label2id=label2id
    )
    
    # Create datasets
    train_dataset = SlotNERDataset(train_texts, train_labels, tokenizer)
    val_dataset = SlotNERDataset(val_texts, val_labels, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir='slot_ner_model_enhanced',
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
        data_collator=DataCollatorForTokenClassification(tokenizer),
    )
    
    # Train model
    print("🚀 Starting training...")
    trainer.train()
    
    # Save model
    model.save_pretrained('slot_ner_model_enhanced')
    tokenizer.save_pretrained('slot_ner_model_enhanced')
    
    # Save label mappings
    import pickle
    with open('slot_ner_model_enhanced/label2id.json', 'w') as f:
        json.dump(label2id, f)
    
    with open('slot_ner_model_enhanced/id2label.json', 'w') as f:
        json.dump(id2label, f)
    
    print(f"\n✅ Training completed!")
    print(f"📊 Model saved to: slot_ner_model_enhanced")
    
    return model, tokenizer

if __name__ == "__main__":
    train_slot_ner_model()
