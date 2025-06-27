"""
Module: flightapi_fetcher.py
Purpose: Fetches flight meta-search data and airline ratings from FlightAPI.
"""

import os
import requests
from dotenv import load_dotenv

# Use new API key and endpoint
FLIGHTAPI_KEY = "68228e48c983a784aa72f5aa"
BASE_URL = "https://api.flightsapi.io"

def fetch_flight_data(origin=None, destination=None, date=None, adults=1, children=0):
    """
    Fetches flight data from FlightsAPI using the /flights/one-way endpoint.
    Args:
        origin (str): IATA code of origin airport.
        destination (str): IATA code of destination airport.
        date (str): Date of travel (DD-MM-YYYY).
        adults (int): Number of adults.
        children (int): Number of children.
    Returns:
        dict: Flight data including prices and airline info, or error message.
    """
    url = "https://api.flightsapi.io/flights/one-way"
    params = {
        "api_key": "68228e48c983a784aa72f5aa",
        "departure_airport": origin,
        "arrival_airport": destination,
        "departure_date": date,
        "adults": adults,
        "children": children
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error {response.status_code}: {response.text}"}
