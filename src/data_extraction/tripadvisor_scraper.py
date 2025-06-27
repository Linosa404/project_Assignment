"""
Module: tripadvisor_scraper.py
Purpose: Extracts travel-relevant arguments and reviews from TripAdvisor articles and user reviews.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def fetch_tripadvisor_article(url, proxies=None):
    """
    Fetches and parses a TripAdvisor article for travel-relevant arguments.
    Args:
        url (str): URL of the TripAdvisor article.
        proxies (dict, optional): Proxy settings for requests.
    Returns:
        list of str: Extracted argument sentences.
    """
    try:
        response = requests.get(url, headers=HEADERS, proxies=proxies, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Focus on main content: look for travel tips, advice, or review sections
        main_content = []
        # Try to find sections with travel tips or advice
        for section in soup.find_all(['section', 'article', 'div'], class_=lambda x: x and ('tips' in x or 'advice' in x or 'content' in x)):
            for tag in section.find_all(['p', 'li']):
                text = tag.get_text(strip=True)
                if len(text) > 50 and text not in main_content:
                    main_content.append(text)
        # Fallback: get all <li> and <p> tags with travel-related keywords
        if not main_content:
            keywords = ['travel', 'tip', 'advice', 'recommend', 'avoid', 'should', 'must', 'important']
            for tag in soup.find_all(['p', 'li']):
                text = tag.get_text(strip=True)
                if any(k in text.lower() for k in keywords) and len(text) > 50 and text not in main_content:
                    main_content.append(text)
        return main_content
    except Exception as e:
        print(f"TripAdvisor article extraction error: {e}")
        return []

def fetch_tripadvisor_reviews(hotel_url, proxies=None):
    """
    Fetches and parses user reviews from a TripAdvisor hotel page.
    Args:
        hotel_url (str): URL of the TripAdvisor hotel page.
        proxies (dict, optional): Proxy settings for requests.
    Returns:
        list of str: Extracted review texts.
    """
    try:
        response = requests.get(hotel_url, headers=HEADERS, proxies=proxies, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []
        for cls in ['QewHA H4 _a', 'reviewText', 'location-review-review-list-parts-ExpandableReview__reviewText--gOmRC']:
            for r in soup.find_all('q', class_=cls):
                text = r.get_text(strip=True)
                if text and text not in reviews:
                    reviews.append(text)
        if not reviews:
            for r in soup.find_all('q'):
                text = r.get_text(strip=True)
                if text and text not in reviews:
                    reviews.append(text)
        return reviews
    except Exception as e:
        print(f"TripAdvisor review extraction error: {e}")
        return []
