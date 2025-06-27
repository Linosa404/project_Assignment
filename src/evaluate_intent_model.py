"""
Evaluate the trained intent model on the validation set.
Computes accuracy and F1-score.
"""
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split

MODEL_PATH = "intent_model"
DATA_PATH = "data/intent_slot_dataset.jsonl"

# Load data
def load_data(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def main():
    data = load_data(DATA_PATH)
    _, val_data = train_test_split(data, test_size=0.2, random_state=42)
    with open(f"{MODEL_PATH}/intent2id.json") as f:
        intent2id = json.load(f)
    id2intent = {v: k for k, v in intent2id.items()}
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    y_true = []
    y_pred = []
    for item in val_data:
        text = item['text']
        true_label = intent2id[item['intent']]
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        y_true.append(true_label)
        y_pred.append(pred)
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted')
    print(f"Accuracy: {acc:.4f}")
    print(f"F1-score (weighted): {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=[id2intent[i] for i in sorted(id2intent.keys())]))

if __name__ == "__main__":
    main()
