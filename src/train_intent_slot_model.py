"""
Train a transformer model for intent and slot extraction from travel questions.
Dataset: data/intent_slot_dataset.jsonl
Model: Hugging Face Transformers (BERT/DistilBERT)
"""
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

MODEL_NAME = "distilbert-base-uncased"
DATA_PATH = "data/intent_slot_dataset.jsonl"

class IntentSlotDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=64):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.intent2id = {intent: i for i, intent in enumerate(sorted(set(d['intent'] for d in data)))}
        self.id2intent = {i: intent for intent, i in self.intent2id.items()}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        encoding = self.tokenizer(item['text'], truncation=True, padding='max_length', max_length=self.max_len, return_tensors='pt')
        intent_id = self.intent2id[item['intent']]
        return {**{k: v.squeeze(0) for k, v in encoding.items()}, 'labels': torch.tensor(intent_id)}

def load_data(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def main():
    data = load_data(DATA_PATH)
    train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds = IntentSlotDataset(train_data, tokenizer)
    val_ds = IntentSlotDataset(val_data, tokenizer)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(train_ds.intent2id))
    args = TrainingArguments(
        output_dir="intent_model_out",
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=8,
        learning_rate=3e-5,
        weight_decay=0.01,
        warmup_steps=200,
        logging_dir="intent_logs",
        logging_steps=10,
        save_total_limit=2,
        eval_strategy="steps",
        eval_steps=100,
        save_steps=100,
        load_best_model_at_end=True
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
    )
    trainer.train()
    model.save_pretrained("intent_model")
    tokenizer.save_pretrained("intent_model")
    # Save intent label mapping
    with open("intent_model/intent2id.json", "w") as f:
        json.dump(train_ds.intent2id, f)

if __name__ == "__main__":
    main()
