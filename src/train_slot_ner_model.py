"""
Train a token classification (NER) model for slot extraction from travel questions.
Dataset: data/slot_ner_dataset.jsonl
Model: Hugging Face Transformers (BERT/DistilBERT)
"""
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForTokenClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

MODEL_NAME = "bert-base-cased"  # Upgraded from distilbert-base-uncased
DATA_PATH = "data/slot_ner_dataset_merged_plus_germeval.jsonl"

class SlotNERDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=64, label2id=None):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.label2id = label2id or self.build_label2id()
        self.id2label = {i: l for l, i in self.label2id.items()}

    def build_label2id(self):
        labels = set()
        for d in self.data:
            for _, _, label in d['labels']:
                labels.add(label)
        label2id = {"O": 0}
        for i, l in enumerate(sorted(labels), 1):
            label2id[f"B-{l}"] = i * 2 - 1
            label2id[f"I-{l}"] = i * 2
        return label2id

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        tokens = self.tokenizer(item['text'], truncation=True, padding='max_length', max_length=self.max_len, return_offsets_mapping=True)
        labels = [0] * self.max_len
        for start, end, label in item['labels']:
            label = label.strip()
            first_token_found = False
            for i, (tok_start, tok_end) in enumerate(tokens['offset_mapping']):
                if tok_start >= start and tok_end <= end:
                    if not first_token_found:
                        # First token in the span gets B-<label>
                        if f"B-{label}" in self.label2id:
                            labels[i] = self.label2id[f"B-{label}"]
                        else:
                            raise KeyError(f"Label '{label}' not found as B-{label} in label2id mapping. Available keys: {list(self.label2id.keys())}")
                        first_token_found = True
                    else:
                        # Subsequent tokens get I-<label>
                        if f"I-{label}" in self.label2id:
                            labels[i] = self.label2id[f"I-{label}"]
                        else:
                            raise KeyError(f"Label '{label}' not found as I-{label} in label2id mapping. Available keys: {list(self.label2id.keys())}")
        tokens = {k: torch.tensor(v) for k, v in tokens.items() if k != 'offset_mapping'}
        return {**tokens, 'labels': torch.tensor(labels)}

def load_data(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def main():
    data = load_data(DATA_PATH)
    train_data, val_data = train_test_split(data, test_size=0.1, random_state=42)  # Use more data for training
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds = SlotNERDataset(train_data, tokenizer)
    val_ds = SlotNERDataset(val_data, tokenizer, label2id=train_ds.label2id)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME, num_labels=len(train_ds.label2id), id2label=train_ds.id2label, label2id=train_ds.label2id)
    args = TrainingArguments(
        output_dir="slot_ner_model_out",
        per_device_train_batch_size=16,  # Larger batch size
        per_device_eval_batch_size=16,
        num_train_epochs=8,  # More epochs
        learning_rate=3e-5,  # Explicit learning rate
        weight_decay=0.01,   # Add weight decay
        logging_dir="slot_ner_logs",
        logging_steps=10,
        save_total_limit=1
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
    )
    trainer.train(resume_from_checkpoint=True)  # Always start fresh to avoid label size mismatch
    # Force CPU for debugging and evaluation
    device = torch.device("cpu")
    model.to(device)
    # Ensure Trainer uses CPU for evaluation
    if torch.backends.mps.is_available():
        import os
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
        torch.mps.empty_cache()
    # After training, evaluate on validation set
    print("Evaluating on validation set...")
    # Manually evaluate on CPU to avoid device mismatch
    val_loader = DataLoader(val_ds, batch_size=4)
    model.eval()
    all_preds = []
    all_labels = []
    for batch in val_loader:
        # Move all tensors to CPU
        batch = {k: v.cpu() for k, v in batch.items()}
        inputs = {k: v for k, v in batch.items() if k != 'labels'}
        with torch.no_grad():
            outputs = model(**inputs).logits
            preds = torch.argmax(outputs, dim=2)
        all_preds.extend(preds.tolist())
        all_labels.extend(batch['labels'].tolist())
    # Simple accuracy metric
    correct = 0
    total = 0
    for pred, label in zip(all_preds, all_labels):
        for p, l in zip(pred, label):
            if l != 0:  # Ignore 'O' labels for accuracy
                total += 1
                if p == l:
                    correct += 1
    accuracy = correct / total if total > 0 else 0
    print(f"Validation token accuracy (ignoring 'O'): {accuracy:.4f}")
    # Print predictions for a batch
    val_loader = DataLoader(val_ds, batch_size=4)
    for batch in val_loader:
        batch = {k: v.cpu() for k, v in batch.items()}
        inputs = {k: v for k, v in batch.items() if k != 'labels'}
        with torch.no_grad():
            outputs = model(**inputs).logits
            preds = torch.argmax(outputs, dim=2)
        for i in range(preds.shape[0]):
            tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][i])
            pred_labels = [val_ds.id2label.get(int(p), 'O') for p in preds[i].tolist()]
            print("Text:", tokenizer.decode(inputs['input_ids'][i], skip_special_tokens=True))
            print("Predicted labels:", pred_labels)
            print("True labels:", batch['labels'][i].tolist())
            print("---")
        break  # Only print first batch
    model.save_pretrained("slot_ner_model")
    tokenizer.save_pretrained("slot_ner_model")
    with open("slot_ner_model/label2id.json", "w") as f:
        json.dump(train_ds.label2id, f)

if __name__ == "__main__":
    main()
