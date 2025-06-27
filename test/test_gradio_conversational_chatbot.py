import sys
import os
import traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from gradio_conversational_chatbot import chat_fn

def run_test_case(message):
    try:
        response = chat_fn(message, history=None)
        print(f"Input: {message}\nResponse: {response}\n{'-'*40}")
    except Exception as e:
        print(f"Error for input: {message}\n{traceback.format_exc()}\n{'-'*40}")

test_cases = [
    "Find flights from Berlin to Rome from July 1 to July 10",
    "What's the weather in London from December 16 to 23, 2025?",
    "Book a hotel in Paris for 2 adults and 1 child from August 5 to August 10",
    "Show me parks in Munich",
    "Random unrelated question",
    "",
    None,
    # German scenarios
    "Finde Flüge von Berlin nach Rom vom 1. Juli bis 10. Juli",
    "Wie ist das Wetter in London vom 16. bis 23. Dezember 2025?",
    "Buche ein Hotel in Paris für 2 Erwachsene und 1 Kind vom 5. bis 10. August",
    "Zeig mir Parks in München",
    "Ich möchte einen Flug von München nach Wien am 15. August buchen",
    "Wie ist die Temperatur in Berlin nächste Woche?",
    "Gibt es günstige Flüge von Frankfurt nach Madrid im September?",
    "Brauche ein Hotel in Hamburg vom 10. bis 15. Oktober mit Frühstück",
    "Was kostet ein Flug von Düsseldorf nach Zürich am 20. Juli?",
    "Wettervorhersage für Köln vom 1. bis 3. März",
    "Finde Flüge von Stuttgart nach Barcelona für 2 Erwachsene am 12. April",
    "Hotel in München für 1 Erwachsenen und 2 Kinder vom 3. bis 7. Mai",
    "Wie ist das Wetter in Paris am 14. Februar?",
    "Flug von Bremen nach Oslo am 22. Dezember gesucht",
    "Gibt es Hotels in Wien mit Parkmöglichkeit vom 8. bis 12. Juni?",
    "Ich brauche einen Flug von Hannover nach Prag am 30. September",
    "Buche ein Hotel in Düsseldorf für 3 Nächte ab dem 5. November"
]

if __name__ == "__main__":
    for msg in test_cases:
        run_test_case(msg if msg is not None else "")
