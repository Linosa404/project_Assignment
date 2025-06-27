import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_extraction.travel_advisor_api import get_travel_advice

TEST_QUERIES = [
    "berlin",
    "hotels berlin",
    "restaurants berlin",
    "paris",
    "new york",
    "rome"
]

def debug_travel_advisor_api():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        result = get_travel_advice(query)
        print(f"Result:\n{result}")

if __name__ == "__main__":
    debug_travel_advisor_api()
