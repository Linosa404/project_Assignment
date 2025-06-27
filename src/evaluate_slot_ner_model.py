"""
Evaluate the trained slot NER model on the validation/test set.
Computes precision, recall, and F1-score for each slot type and overall.
"""
import json
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from sklearn.metrics import precision_recall_fscore_support, classification_report
from train_slot_ner_model import SlotNERDataset, load_data, MODEL_NAME, DATA_PATH
from sklearn.model_selection import train_test_split

MODEL_PATH = "slot_ner_model"
MAX_LEN = 64

def align_labels(preds, labels, id2label):
    # Remove padding and align predictions with true labels
    true_labels = []
    pred_labels = []
    for p_seq, l_seq in zip(preds, labels):
        for p, l in zip(p_seq, l_seq):
            if l != 0:  # Ignore 'O' and padding
                true_labels.append(id2label[l])
                pred_labels.append(id2label[p])
    return true_labels, pred_labels

def main():
    # Load data and split
    data = load_data(DATA_PATH)
    _, val_data = train_test_split(data, test_size=0.2, random_state=42)
    # Load model and tokenizer
    with open(f"{MODEL_PATH}/label2id.json") as f:
        label2id = json.load(f)
    id2label = {v: k for k, v in label2id.items()}
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    model.eval()
    # Prepare dataset
    val_ds = SlotNERDataset(val_data, tokenizer, label2id=label2id)
    all_true = []
    all_pred = []
    for i in range(len(val_ds)):
        item = val_ds[i]
        input_ids = item['input_ids'].unsqueeze(0)
        attention_mask = item['attention_mask'].unsqueeze(0)
        labels = item['labels'].tolist()
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=2)[0].tolist()
        all_true.append(labels)
        all_pred.append(preds)
    # Align and flatten
    true_labels, pred_labels = align_labels(all_pred, all_true, id2label)
    print(classification_report(true_labels, pred_labels, zero_division=0))

if __name__ == "__main__":
    main()
