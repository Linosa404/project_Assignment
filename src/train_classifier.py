"""
train_classifier.py
Train a simple classifier (demo: fine-tune transformers or use sklearn) on collected travel data.
"""
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Load data
with open("data/collected_travel_data.json") as f:
    data = json.load(f)

# For demo: classify booking vs tripadvisor (replace with pro/contra if labeled)
texts = [d["text"] for d in data if d["type"] in ["booking", "tripadvisor"]]
labels = [d["type"] for d in data if d["type"] in ["booking", "tripadvisor"]]

# Split
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Vectorize
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_vec, y_train)

# Evaluate
y_pred = clf.predict(X_test_vec)
print(classification_report(y_test, y_pred))

# Save model
import pickle
with open("data/travel_classifier.pkl", "wb") as f:
    pickle.dump((vectorizer, clf), f)
print("Model trained and saved to data/travel_classifier.pkl")
