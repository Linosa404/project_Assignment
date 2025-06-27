"""
kiwi_api.py - Integration with Kiwi.com (Skypicker) API for flight search
Docs: https://docs.kiwi.com/
"""
import requests

KIWI_API_KEY = None  # Set this at runtime or via environment variable
BASE_URL = "https://api.tequila.kiwi.com"

def set_kiwi_api_key(key):
    global KIWI_API_KEY
    KIWI_API_KEY = key

def search_flights_one_way(origin, destination, date, adults=1, children=0, infants=0, cabin_class="M", currency="USD"): 
    """
    Search for one-way flights.
    origin, destination: IATA codes
    date: YYYY-MM-DD
    """
    url = f"{BASE_URL}/v2/search"
    headers = {"apikey": KIWI_API_KEY}
    params = {
        "fly_from": origin,
        "fly_to": destination,
        "date_from": date,
        "date_to": date,
        "adults": adults,
        "children": children,
        "infants": infants,
        "selected_cabins": cabin_class,
        "curr": currency,
        "limit": 10
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error {response.status_code}: {response.text}"}

def search_flights_round_trip(origin, destination, depart_date, return_date, adults=1, children=0, infants=0, cabin_class="M", currency="USD"):
    """
    Search for round-trip flights.
    depart_date, return_date: YYYY-MM-DD
    """
    url = f"{BASE_URL}/v2/search"
    headers = {"apikey": KIWI_API_KEY}
    params = {
        "fly_from": origin,
        "fly_to": destination,
        "date_from": depart_date,
        "date_to": depart_date,
        "return_from": return_date,
        "return_to": return_date,
        "adults": adults,
        "children": children,
        "infants": infants,
        "selected_cabins": cabin_class,
        "curr": currency,
        "limit": 10
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error {response.status_code}: {response.text}"}

def search_flights_multi_city(routes, adults=1, children=0, infants=0, cabin_class="M", currency="USD"):
    """
    Search for multi-city flights.
    routes: list of dicts [{"from": IATA, "to": IATA, "date": YYYY-MM-DD}, ...]
    """
    url = f"{BASE_URL}/v2/search"
    headers = {"apikey": KIWI_API_KEY}
    # Build the parameters for multi-city
    params = {
        "adults": adults,
        "children": children,
        "infants": infants,
        "selected_cabins": cabin_class,
        "curr": currency,
        "limit": 10
    }
    for idx, route in enumerate(routes):
        params[f"fly_from[{idx}]"] = route["from"]
        params[f"fly_to[{idx}]"] = route["to"]
        params[f"date_from[{idx}]"] = route["date"]
        params[f"date_to[{idx}]"] = route["date"]
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error {response.status_code}: {response.text}"}
