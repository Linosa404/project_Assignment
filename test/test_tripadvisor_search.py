import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_extraction.tripadvisor_search import search_tripadvisor

TEST_QUERIES = [
    "berlin",
    "hotels berlin",
    "restaurants berlin",
    "rent car berlin",
    "new york",
    "hotels new york",
    "restaurants new york",
    "rent car new york",
    "paris",
    "hotels paris",
    "restaurants paris",
    "rent car paris"
]

def debug_tripadvisor_api():
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        result = search_tripadvisor(query, debug=True)
        print(f"Result:\n{result}")

if __name__ == "__main__":
    debug_tripadvisor_api()
