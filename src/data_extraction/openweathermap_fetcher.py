"""
Module: openweathermap_fetcher.py
Purpose: Fetches weather data from OpenWeatherMap for travel argument extraction.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

def fetch_weather_data(api_key=None, location=None, date=None):
    """
    Fetches weather data for a given location (and optionally date) from OpenWeatherMap.
    Args:
        api_key (str): OpenWeatherMap API key. If None, uses env variable.
        location (str): City name or coordinates.
        date (str, optional): Date for historical weather (YYYY-MM-DD). If None, fetch current weather.
    Returns:
        dict: Weather data.
    """
    if api_key is None:
        api_key = OPENWEATHER_KEY
    if not (api_key and location):
        return {"error": "Missing required parameters."}
    base_url = "https://api.openweathermap.org/data/2.5/"
    if date:
        # For historical data, use the One Call API (requires paid plan)
        # This is a placeholder; actual implementation may differ
        url = f"{base_url}onecall/timemachine?lat={location['lat']}&lon={location['lon']}&dt={date}&appid={api_key}"
    else:
        url = f"{base_url}weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
