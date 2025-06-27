"""
Module: argument_classifier.py
Purpose: Classifies extracted arguments as Pro or Contra using a Natural Language Inference (NLI) model.
"""

from transformers import pipeline

# Load a pre-trained NLI model (e.g., roberta-large-mnli)
nli = pipeline("text-classification", model="roberta-large-mnli")

def classify_argument(argument, topic, pro_hypothesis, contra_hypothesis):
    """
    Classifies an argument as Pro or Contra for a given topic using NLI.
    Args:
        argument (str): The extracted argument sentence.
        topic (str): The topic (e.g., 'flights', 'hotels').
        pro_hypothesis (str): Hypothesis for Pro (e.g., 'This is a good reason for flights').
        contra_hypothesis (str): Hypothesis for Contra (e.g., 'This is a bad reason for flights').
    Returns:
        str: 'pro', 'contra', or 'neutral'.
    """
    pro_result = nli(argument, text_pair=pro_hypothesis)[0]
    contra_result = nli(argument, text_pair=contra_hypothesis)[0]
    if pro_result['label'] == 'ENTAILMENT' and pro_result['score'] > 0.7:
        return 'pro'
    elif contra_result['label'] == 'ENTAILMENT' and contra_result['score'] > 0.7:
        return 'contra'
    else:
        return 'neutral'

# Example usage:
# classify_argument("Direct flights are faster and more convenient.", "flights", "This is a good reason for flights.", "This is a bad reason for flights.")
