import requests
import time

def get_location_id(query):
    url = "https://travel-advisor.p.rapidapi.com/locations/auto-complete"
    params = {"query": query, "lang": "en_US", "units": "km"}
    headers = {
        "x-rapidapi-key": "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738",
        "x-rapidapi-host": "travel-advisor.p.rapidapi.com"
    }
    for _ in range(3):
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("data", []):
                if item.get("result_type") == "geos":
                    return item.get("result_object", {}).get("location_id")
            # fallback: try first result
            if data.get("data"):
                return data["data"][0].get("result_object", {}).get("location_id")
        elif resp.status_code == 429:
            time.sleep(5)
        else:
            break
    return None

def get_hotels(location_id):
    url = "https://travel-advisor.p.rapidapi.com/hotels/list"
    params = {"location_id": location_id, "adults": "1", "rooms": "1", "nights": "2", "offset": "0", "currency": "USD", "order": "asc", "limit": "3", "sort": "recommended", "lang": "en_US"}
    headers = {
        "x-rapidapi-key": "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738",
        "x-rapidapi-host": "travel-advisor.p.rapidapi.com"
    }
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        return [h for h in data.get("data", []) if h.get("name")]  # filter only hotels with names
    return []

def get_restaurants(location_id):
    url = "https://travel-advisor.p.rapidapi.com/restaurants/list"
    params = {"location_id": location_id, "currency": "USD", "lunit": "km", "limit": "3", "open_now": "false", "lang": "en_US"}
    headers = {
        "x-rapidapi-key": "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738",
        "x-rapidapi-host": "travel-advisor.p.rapidapi.com"
    }
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        return [r for r in data.get("data", []) if r.get("name")]  # filter only restaurants with names
    return []

def get_attractions(location_id):
    url = "https://travel-advisor.p.rapidapi.com/attractions/list"
    params = {"location_id": location_id, "currency": "USD", "lang": "en_US", "lunit": "km", "sort": "recommended", "limit": "3"}
    headers = {
        "x-rapidapi-key": "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738",
        "x-rapidapi-host": "travel-advisor.p.rapidapi.com"
    }
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        return [a for a in data.get("data", []) if a.get("name")]  # filter only attractions with names
    return []

def get_travel_advice(query):
    location_id = get_location_id(query)
    if not location_id:
        return "No TripAdvisor results found."
    hotels = get_hotels(location_id)
    restaurants = get_restaurants(location_id)
    attractions = get_attractions(location_id)
    advice = []
    if hotels:
        advice.append("Top Hotels:\n" + "\n".join([f"🏨 {h['name']} ({h.get('rating', '?')}⭐)" for h in hotels]))
    if restaurants:
        advice.append("Top Restaurants:\n" + "\n".join([f"🍽️ {r['name']} ({r.get('rating', '?')}⭐)" for r in restaurants]))
    if attractions:
        advice.append("Top Attractions:\n" + "\n".join([f"📍 {a['name']} ({a.get('rating', '?')}⭐)" for a in attractions]))
    if not advice:
        return "No TripAdvisor results found."
    return "\n\n".join(advice)
