#!/usr/bin/env python3
"""
Prepare final datasets for training and create updated training scripts
"""
import json

def create_specialized_datasets():
    """Create intent and slot NER datasets from final training data"""
    
    print("📊 Creating specialized training datasets...")
    
    # Read final dataset
    with open('data/final_training_dataset.jsonl', 'r', encoding='utf-8') as f:
        entries = [json.loads(line) for line in f if line.strip()]
    
    print(f"📄 Total entries: {len(entries)}")
    
    # Create intent dataset
    intent_entries = [e for e in entries if e.get('intent')]
    intent_file = 'data/final_intent_dataset.jsonl'
    
    with open(intent_file, 'w', encoding='utf-8') as f:
        for entry in intent_entries:
            output_entry = {
                'text': entry['text'],
                'intent': entry['intent']
            }
            f.write(json.dumps(output_entry, ensure_ascii=False) + '\n')
    
    print(f"🎯 Intent dataset: {len(intent_entries)} entries → {intent_file}")
    
    # Create slot NER dataset
    slot_entries = [e for e in entries if e.get('slots')]
    slot_file = 'data/final_slot_ner_dataset.jsonl'
    
    with open(slot_file, 'w', encoding='utf-8') as f:
        for entry in slot_entries:
            # Convert to NER format with entities
            entities = []
            for slot_key, slot_value in entry['slots'].items():
                entities.append({
                    'entity': slot_key,
                    'value': slot_value
                })
            
            output_entry = {
                'text': entry['text'],
                'entities': entities
            }
            f.write(json.dumps(output_entry, ensure_ascii=False) + '\n')
    
    print(f"🏷️  Slot NER dataset: {len(slot_entries)} entries → {slot_file}")
    
    # Print statistics
    intent_counts = {}
    for entry in intent_entries:
        intent = entry['intent']
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    print(f"\n📈 Intent distribution ({len(intent_entries)} total):")
    for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(intent_entries)) * 100
        print(f"  {intent}: {count} ({percentage:.1f}%)")
    
    return intent_file, slot_file

def create_training_scripts():
    """Create updated training scripts with optimal parameters"""
    
    # Intent training script
    intent_script = """#!/usr/bin/env python3
\"\"\"
Enhanced Intent Classification Training Script
Optimized for 80% accuracy target
\"\"\"
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
    \"\"\"Load intent classification data\"\"\"
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
    \"\"\"Train intent classification model\"\"\"
    
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
    print(f"\\n✅ Training completed!")
    print(f"📊 Validation Accuracy: {accuracy:.3f}")
    
    # Detailed classification report
    intent_names = label_encoder.classes_
    print(f"\\n📈 Detailed Classification Report:")
    print(classification_report(val_labels, pred_labels, target_names=intent_names))
    
    return model, tokenizer, label_encoder

if __name__ == "__main__":
    train_intent_model()
"""
    
    with open('train_enhanced_intent_model.py', 'w', encoding='utf-8') as f:
        f.write(intent_script)
    
    # Slot NER training script
    slot_script = """#!/usr/bin/env python3
\"\"\"
Enhanced Slot NER Training Script
Optimized for 80% accuracy target
\"\"\"
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
    \"\"\"Create BIO labels for NER\"\"\"
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
    \"\"\"Load slot NER data\"\"\"
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
    \"\"\"Train slot NER model\"\"\"
    
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
    
    print(f"\\n✅ Training completed!")
    print(f"📊 Model saved to: slot_ner_model_enhanced")
    
    return model, tokenizer

if __name__ == "__main__":
    train_slot_ner_model()
"""
    
    with open('train_enhanced_slot_ner_model.py', 'w', encoding='utf-8') as f:
        f.write(slot_script)
    
    print("✅ Training scripts created:")
    print("  🎯 train_enhanced_intent_model.py")
    print("  🏷️  train_enhanced_slot_ner_model.py")

if __name__ == "__main__":
    print("🎯 Preparing final datasets and training scripts...")
    intent_file, slot_file = create_specialized_datasets()
    create_training_scripts()
    print("\n🎉 Dataset preparation completed!")
    print("\n🚀 Next steps:")
    print("  1. Run: python3 train_enhanced_intent_model.py")
    print("  2. Run: python3 train_enhanced_slot_ner_model.py")
    print("  3. Test improved accuracy")
