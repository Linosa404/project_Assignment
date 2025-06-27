"""
Pipeline: extract_and_classify.py
Purpose: Extracts travel arguments from sources and classifies them as Pro/Contra for each topic.
"""

from src.data_extraction import booking_scraper, tripadvisor_scraper
from src.argument_classifier import classify_argument

# Define topics and hypotheses for NLI
TOPICS = {
    "flights": {
        "pro": "This is a good reason for flights.",
        "contra": "This is a bad reason for flights."
    },
    "destinations": {
        "pro": "This is a good reason for this destination.",
        "contra": "This is a bad reason for this destination."
    },
    "restrictions": {
        "pro": "This is a good reason for travel restrictions.",
        "contra": "This is a bad reason for travel restrictions."
    },
    "accommodations": {
        "pro": "This is a good reason for hotels or hostels.",
        "contra": "This is a bad reason for hotels or hostels."
    }
}

# Example URLs (replace with real ones for production)
booking_article_url = "https://www.booking.com/articles/en-gb/tips-for-travelling-with-pets.html"
tripadvisor_article_url = "https://www.tripadvisor.com/Travel-g191-c18213/United-States:Tips.For.Traveling.With.Pets.html"

# Extract arguments from Booking.com
booking_args = booking_scraper.fetch_booking_article(booking_article_url)
# Extract arguments from TripAdvisor
tripadvisor_args = tripadvisor_scraper.fetch_tripadvisor_article(tripadvisor_article_url)

all_args = booking_args + tripadvisor_args

results = {topic: {"pro": [], "contra": [], "neutral": []} for topic in TOPICS}

for arg in all_args:
    for topic, hypos in TOPICS.items():
        label = classify_argument(arg, topic, hypos["pro"], hypos["contra"])
        results[topic][label].append(arg)

# Print summary
for topic in results:
    print(f"\nTopic: {topic}")
    print(f"Pro arguments ({len(results[topic]['pro'])}):")
    for a in results[topic]['pro'][:5]:
        print("  +", a)
    print(f"Contra arguments ({len(results[topic]['contra'])}):")
    for a in results[topic]['contra'][:5]:
        print("  -", a)
    print(f"Neutral arguments ({len(results[topic]['neutral'])}): {len(results[topic]['neutral'])}")
