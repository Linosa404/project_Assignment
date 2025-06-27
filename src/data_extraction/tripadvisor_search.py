import requests
import time
import json
from datetime import datetime, timedelta

RAPIDAPI_KEY = "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738"
RAPIDAPI_HOST = "tripadvisor16.p.rapidapi.com"
BASE_URL = "https://tripadvisor16.p.rapidapi.com/api/v1"

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

def safe_get(url, headers, params=None, timeout=20, retries=3, backoff=2):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
            if resp.status_code == 429:
                time.sleep(5)
                continue
            return resp
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(backoff)
                continue
            return None
        except requests.exceptions.RequestException:
            return None
    return None

def search_tripadvisor(query, type_hint=None, debug=False):
    """
    Search TripAdvisor using the RapidAPI for hotels, restaurants, and rental cars based on the query.
    Returns a summary string for the chatbot. If debug=True, prints raw API responses.
    """
    # Try to find a geoId for the query
    loc_url = f"{BASE_URL}/hotels/searchLocation"
    loc_params = {"query": query}
    loc_resp = safe_get(loc_url, headers=HEADERS, params=loc_params)
    if debug:
        print(f"[DEBUG] Location search response: {getattr(loc_resp, 'status_code', None)}")
        if loc_resp:
            print(loc_resp.text)
    if not loc_resp or loc_resp.status_code != 200:
        return f"TripAdvisor API error (location search): {getattr(loc_resp, 'status_code', 'timeout/error')}"
    loc_data = loc_resp.json()
    if debug:
        print(f"[DEBUG] Location data: {json.dumps(loc_data, indent=2)}")
    if not loc_data.get("data"):
        return "Keine relevanten TripAdvisor-Ergebnisse gefunden."
    location = loc_data["data"][0]
    geo_id = location.get("geoId")
    location_name = location.get("title", query)
    advice = []
    # Prepare dates for hotels and cars
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    checkin = today.strftime("%Y-%m-%d")
    checkout = tomorrow.strftime("%Y-%m-%d")
    # Hotel search (geoId required, plus check-in/check-out)
    hotel_url = f"{BASE_URL}/hotels/searchHotels"
    hotel_params = {"geoId": geo_id, "checkIn": checkin, "checkOut": checkout, "pageNumber": "1", "currencyCode": "USD"}
    hotel_resp = safe_get(hotel_url, headers=HEADERS, params=hotel_params)
    if debug:
        print(f"[DEBUG] Hotel search response: {getattr(hotel_resp, 'status_code', None)}")
        if hotel_resp:
            print(hotel_resp.text)
    if hotel_resp and hotel_resp.status_code == 200 and hotel_resp.json().get("data"):
        hotels = hotel_resp.json()["data"][:3]
        hotel_lines = [f"🏨 {h.get('title')} ({h.get('bubbleRating', {}).get('rating', '?')}⭐): {h.get('primaryInfo', '')}" for h in hotels]
        advice.append(f"Top Hotels in {location_name} laut TripAdvisor:\n" + "\n".join(hotel_lines))
    # Restaurant search (geoId required)
    rest_url = f"{BASE_URL}/restaurant/searchRestaurants"
    rest_params = {"geoId": geo_id}
    rest_resp = safe_get(rest_url, headers=HEADERS, params=rest_params)
    if debug:
        print(f"[DEBUG] Restaurant search response: {getattr(rest_resp, 'status_code', None)}")
        if rest_resp:
            print(rest_resp.text)
    if rest_resp and rest_resp.status_code == 200 and rest_resp.json().get("data"):
        rests = rest_resp.json()["data"][:3]
        rest_lines = [f"🍽️ {r.get('name')} ({r.get('bubbleRating', {}).get('rating', '?')}⭐): {r.get('establishmentTypeAndCuisineTags', [''])[0]}" for r in rests]
        advice.append(f"Top Restaurants in {location_name} laut TripAdvisor:\n" + "\n".join(rest_lines))
    # Rental car search (geoId as pickUpPlaceId, plus dates)
    car_url = f"{BASE_URL}/cars/searchCarsSameDropOff"
    car_params = {"pickUpPlaceId": geo_id, "pickUpDate": checkin, "dropOffDate": checkout, "order": "RECOMMENDED", "page": "1", "currencyCode": "USD"}
    car_resp = safe_get(car_url, headers=HEADERS, params=car_params)
    if debug:
        print(f"[DEBUG] Car search response: {getattr(car_resp, 'status_code', None)}")
        if car_resp:
            print(car_resp.text)
    if car_resp and car_resp.status_code == 200 and car_resp.json().get("data"):
        cars = car_resp.json()["data"][:3]
        car_lines = [f"🚗 {c.get('vehicleInfo', {}).get('name', 'Car')} ({c.get('price', {}).get('display', '?')})" for c in cars]
        advice.append(f"Top Mietwagen laut TripAdvisor:\n" + "\n".join(car_lines))
    if not advice:
        return "Keine relevanten TripAdvisor-Ergebnisse gefunden."
    return "\n\n".join(advice)
