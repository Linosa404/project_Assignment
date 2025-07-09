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
import logging
from config import DEVICE, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

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
        word_labels = self.labels[idx] # These are original word-level labels

        # Tokenize the text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt',
            # is_split_into_words=False # Keep this as False, we'll align later
        )

        # Get word IDs from the tokenizer output to align labels
        word_ids = encoding.word_ids(batch_index=0)
        
        aligned_labels = [-100] * self.max_length # -100 is ignored by PyTorch's CrossEntropyLoss
        previous_word_idx = None

        for i, word_idx in enumerate(word_ids):
            if word_idx is None:
                # Special tokens like [CLS], [SEP], [PAD]
                aligned_labels[i] = -100
            elif word_idx != previous_word_idx:
                # Start of a new word or first token of a word
                if word_idx < len(word_labels):
                    aligned_labels[i] = word_labels[word_idx]
                else:
                    aligned_labels[i] = 0 # O tag if out of bounds (shouldn't happen with correct max_length)
            else:
                # Subsequent token of the same word
                # Use the same label as the first token of the word, or I-tag if appropriate
                if word_idx < len(word_labels):
                    aligned_labels[i] = word_labels[word_idx] # For simplicity, replicating the label. For B-I-O, this would be I-tag
                else:
                    aligned_labels[i] = 0 # O tag

            previous_word_idx = word_idx
        
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
        
        # --- FIX START ---
        # Ensure entity_value is a string before splitting
        entity_value = str(entity_value) 
        # --- FIX END ---
        
        # Find entity in text
        entity_words = entity_value.split()
        for i in range(len(words) - len(entity_words) + 1):
            if ' '.join(words[i:i+len(entity_words)]).lower() == entity_value.lower():
                if len(entity_words) == 1:
                    labels[i] = f'B-{entity_type}'
                else:
                    labels[i] = f'B-{entity_type}'
                    for j in range(1, len(entity_words)):
                        if i + j < len(labels):
                            labels[i + j] = f'I-{entity_type}'
                break # Found and labeled, move to next entity
    
    return [label2id.get(label, 0) for label in labels] # Use 0 for O if label not found

def load_slot_data(file_path):
    """Load slot NER data with BIO tagging"""
    texts = []
    all_labels = []
    
    # Define slot labels
    label_set = set(['O'])  # Start with Outside label
    
    # First pass: collect all possible labels
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                labels = data.get('labels', [])
                label_set.update(labels)
    
    # Create label mappings
    sorted_labels = sorted(list(label_set))
    label2id = {label: idx for idx, label in enumerate(sorted_labels)}
    id2label = {idx: label for label, idx in label2id.items()}
    
    # Second pass: load data
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                text = data['text']
                labels = data.get('labels', ['O'] * len(text.split()))
                
                # Convert labels to IDs
                label_ids = [label2id.get(label, label2id['O']) for label in labels]
                
                texts.append(text)
                all_labels.append(label_ids)
    
    return texts, all_labels, label2id, id2label

def train_slot_ner_model():
    """Train slot NER model"""
    try:
        logger.info("Training slot NER model...")
        
        # Load enhanced data
        texts, labels, label2id, id2label = load_slot_data('data/enhanced_slot_ner_dataset.jsonl')
        print(f"📊 Loaded {len(texts)} training examples")
        print(f"🏷️  Label types: {len(label2id)}")
        print(f"🏷️  Labels: {list(label2id.keys())}")
        
        # Split data with better ratio for large dataset
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.15, random_state=42
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
        ).to(DEVICE) # Move model to the selected device
        
        # Create datasets with appropriate max_length
        train_dataset = SlotNERDataset(train_texts, train_labels, tokenizer, max_length=128)
        val_dataset = SlotNERDataset(val_texts, val_labels, tokenizer, max_length=128)
        
        # Optimal training arguments for slot NER
        training_args = TrainingArguments(
            output_dir='slot_ner_model_enhanced',
            num_train_epochs=6,  # Increased epochs for better NER performance
            per_device_train_batch_size=24,  # Balanced batch size for NER
            per_device_eval_batch_size=48,   # Larger eval batch size
            warmup_steps=800,  # More warmup for large dataset
            weight_decay=0.015,  # Slight regularization
            logging_dir='./logs_slot_ner',
            logging_steps=50,
            eval_strategy='steps',
            eval_steps=400,  # Less frequent evaluation for efficiency
            save_strategy='steps',
            save_steps=800,
            load_best_model_at_end=True,
            metric_for_best_model='eval_f1',  # Use F1 score for NER
            greater_is_better=True,
            save_total_limit=3,
            dataloader_pin_memory=False,  # MPS compatibility
            learning_rate=3e-5,  # Higher learning rate for NER
            lr_scheduler_type='linear',  # Linear schedule works well for NER
            gradient_accumulation_steps=2,  # Effective larger batch size
            fp16=False,  # Disabled for MPS compatibility
            dataloader_num_workers=0,  # MPS compatibility
            seed=42,
            report_to="none",  # Disable wandb logging
            remove_unused_columns=True,
            group_by_length=True,  # Efficiency for variable length sequences
        )
        
        # Add custom metrics computation
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=2)
            
            # Remove ignored index (special tokens)
            true_predictions = [
                [id2label[p] for (p, l) in zip(prediction, label) if l != -100]
                for prediction, label in zip(predictions, labels)
            ]
            true_labels = [
                [id2label[l] for (p, l) in zip(prediction, label) if l != -100]
                for prediction, label in zip(predictions, labels)
            ]
            
            # Compute metrics
            from sklearn.metrics import precision_recall_fscore_support, accuracy_score
            
            # Flatten for sklearn
            flat_true = [item for sublist in true_labels for item in sublist]
            flat_pred = [item for sublist in true_predictions for item in sublist]
            
            precision, recall, f1, _ = precision_recall_fscore_support(flat_true, flat_pred, average='weighted')
            accuracy = accuracy_score(flat_true, flat_pred)
            
            return {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'accuracy': accuracy
            }
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=tokenizer,
            data_collator=DataCollatorForTokenClassification(tokenizer),
            compute_metrics=compute_metrics,
        )
        
        # Train model
        print("🚀 Starting training...")
        trainer.train()
        
        # Save model
        model.save_pretrained('slot_ner_model_enhanced')
        tokenizer.save_pretrained('slot_ner_model_enhanced')
        
        # Save label mappings
        with open('slot_ner_model_enhanced/label2id.json', 'w') as f:
            json.dump(label2id, f, indent=2)
        
        with open('slot_ner_model_enhanced/id2label.json', 'w') as f:
            json.dump(id2label, f, indent=2)
        
        # Final evaluation
        print("\n🧪 Running final evaluation...")
        eval_result = trainer.evaluate()
        
        print(f"\n✅ Training completed!")
        print(f"📊 Final Validation Metrics:")
        print(f"   Accuracy: {eval_result.get('eval_accuracy', 0):.3f} ({eval_result.get('eval_accuracy', 0)*100:.1f}%)")
        print(f"   F1 Score: {eval_result.get('eval_f1', 0):.3f}")
        print(f"   Precision: {eval_result.get('eval_precision', 0):.3f}")
        print(f"   Recall: {eval_result.get('eval_recall', 0):.3f}")
        
        # Check if we met the 80% target
        accuracy = eval_result.get('eval_accuracy', 0)
        if accuracy >= 0.80:
            print("🎉 SUCCESS: Achieved 80%+ accuracy target!")
        else:
            print(f"⚠️ TARGET MISSED: Need {0.80-accuracy:.3f} more accuracy to reach 80%")
        
        print(f"📁 Model saved to: slot_ner_model_enhanced")
        
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error during slot NER model training: {e}")
        raise

if __name__ == "__main__":
    train_slot_ner_model()