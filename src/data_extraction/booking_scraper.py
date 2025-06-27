"""
Module: booking_scraper.py
Purpose: Extracts travel-relevant arguments and theses from Booking.com articles and user reviews.
"""

import requests
from bs4 import BeautifulSoup


def fetch_booking_article(url):
    """
    Fetches and parses a Booking.com article for travel-relevant arguments.
    Args:
        url (str): URL of the Booking.com article.
    Returns:
        list of str: Extracted argument sentences.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Example: Extract all paragraph texts
    paragraphs = soup.find_all('p')
    arguments = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
    return arguments


def fetch_booking_reviews(hotel_url):
    """
    Fetches and parses user reviews from a Booking.com hotel page.
    Args:
        hotel_url (str): URL of the Booking.com hotel page.
    Returns:
        list of str: Extracted review texts.
    """
    response = requests.get(hotel_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Example: Extract review texts (Booking.com structure may change)
    reviews = soup.find_all('span', class_='c-review__body')
    review_texts = [r.get_text(strip=True) for r in reviews]
    return review_texts

# Example usage (to be removed or moved to a test script):
# article_args = fetch_booking_article('https://www.booking.com/articles/...')
# hotel_reviews = fetch_booking_reviews('https://www.booking.com/hotel/...')
