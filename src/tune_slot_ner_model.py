"""
Optuna-based hyperparameter tuning for the slot NER model.
Searches for best learning rate, batch size, and epochs.
"""
import json
import torch
import optuna
from transformers import AutoTokenizer, AutoModelForTokenClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from train_slot_ner_model import SlotNERDataset, load_data, MODEL_NAME, DATA_PATH
import numpy as np

MODEL_PATH = "slot_ner_model"


def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=2)
    labels = p.label_ids
    mask = labels != 0
    correct = (preds[mask] == labels[mask]).sum()
    total = mask.sum()
    return {"accuracy": correct / total if total > 0 else 0}


def objective(trial):
    # Hyperparameter search space
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-4, log=True)
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
    num_train_epochs = trial.suggest_int("num_train_epochs", 3, 8)

    data = load_data(DATA_PATH)
    train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds = SlotNERDataset(train_data, tokenizer)
    val_ds = SlotNERDataset(val_data, tokenizer, label2id=train_ds.label2id)
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(train_ds.label2id),
        id2label=train_ds.id2label,
        label2id=train_ds.label2id
    )
    args = TrainingArguments(
        output_dir="tune_tmp",
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        logging_dir="tune_logs",
        logging_steps=20,
        save_total_limit=1,
        disable_tqdm=True,
        report_to=[]
    )
    # Manually evaluate after training since eval_strategy is not available
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    eval_result = trainer.evaluate()
    return eval_result["eval_accuracy"]


def main():
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=15)
    print("Best trial:")
    print(study.best_trial)
    print("Best hyperparameters:")
    print(study.best_params)

if __name__ == "__main__":
    main()
