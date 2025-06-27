"""
flight_apis.py - Unified access to both Kiwi.com (RapidAPI) and Google Flights (RapidAPI)
"""
import http.client
import urllib.parse

# --- Kiwi.com Cheap Flights (RapidAPI) ---
KIWI_RAPIDAPI_KEY = "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738"
KIWI_RAPIDAPI_HOST = "kiwi-com-cheap-flights.p.rapidapi.com"

def kiwi_one_way(params):
    conn = http.client.HTTPSConnection(KIWI_RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': KIWI_RAPIDAPI_KEY,
        'x-rapidapi-host': KIWI_RAPIDAPI_HOST
    }
    query = "/one-way?" + urllib.parse.urlencode(params)
    conn.request("GET", query, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

def kiwi_round_trip(params):
    conn = http.client.HTTPSConnection(KIWI_RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': KIWI_RAPIDAPI_KEY,
        'x-rapidapi-host': KIWI_RAPIDAPI_HOST
    }
    query = "/round-trip?" + urllib.parse.urlencode(params)
    conn.request("GET", query, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

# --- Google Flights (RapidAPI) ---
GOOGLE_RAPIDAPI_KEY = KIWI_RAPIDAPI_KEY
GOOGLE_RAPIDAPI_HOST = "google-flights2.p.rapidapi.com"

def google_flights_request(endpoint, params=None):
    conn = http.client.HTTPSConnection(GOOGLE_RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': GOOGLE_RAPIDAPI_KEY,
        'x-rapidapi-host': GOOGLE_RAPIDAPI_HOST
    }
    path = endpoint
    if params:
        path += "?" + urllib.parse.urlencode(params)
    conn.request("GET", path, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

# Example endpoints for Google Flights:
# /api/v1/checkServer
# /api/v1/searchAirport
# /api/v1/getCalendarPicker
# /api/v1/searchFlights
# /api/v1/getNextFlights
# /api/v1/getBookingDetails
# /api/v1/getBookingURL
# /api/v1/getPriceGraph
# /api/v1/getCalendarGrid
