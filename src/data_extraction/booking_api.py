import http.client
import urllib.parse
import json
from datetime import datetime

RAPIDAPI_KEY = "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738"
RAPIDAPI_HOST = "booking-com.p.rapidapi.com"


def search_hotels(city, checkin_date, checkout_date, adults=1, children=0, rooms=1, locale="en-gb", currency="EUR"): 
    """
    Search for hotels using Booking.com API via RapidAPI.
    Returns a list of hotel dicts with name, address, price, rating, etc.
    """
    import logging
    logging.basicConfig(filename='log/hotel_debug.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
    # Step 1: Get destination_id for the city
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({
        "name": city,
        "locale": locale
    })
    conn.request("GET", f"/v1/hotels/locations?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    locations = json.loads(data.decode("utf-8"))
    logging.debug(f"locations response for city '{city}': {locations}")
    if not locations or not isinstance(locations, list) or not locations[0].get('dest_id'):
        logging.debug(f"No dest_id found for city '{city}'. Raw response: {locations}")
        return []
    dest_id = locations[0]["dest_id"]

    # Step 2: Search for hotels
    # Ensure children_number is at least 1 (API requires >=1)
    children_number = max(children, 1)
    params = urllib.parse.urlencode({
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "dest_id": dest_id,
        "dest_type": "city",
        "adults_number": adults,
        "children_number": children_number,
        "room_number": rooms,
        "order_by": "popularity",
        "locale": locale,
        "currency": currency,
        "filter_by_currency": currency,
        "units": "metric"
    })
    conn.request("GET", f"/v1/hotels/search?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    hotels = json.loads(data.decode("utf-8"))
    logging.debug(f"hotels search response for city '{city}': {hotels}")
    return hotels.get("result", [])

def get_exchange_rates(currency="EUR", locale="en-gb"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({"currency": currency, "locale": locale})
    conn.request("GET", f"/v1/metadata/exchange-rates?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_children_policies(hotel_id, children_age=5, locale="en-gb"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({"locale": locale, "hotel_id": hotel_id, "children_age": children_age})
    conn.request("GET", f"/v1/hotels/children-policies?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def search_hotels_by_coordinates(latitude, longitude, checkin_date, checkout_date, adults=1, children=0, rooms=1, locale="en-gb", currency="EUR", categories_filter_ids=None, children_ages=None):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = {
        "room_number": rooms,
        "children_number": children,
        "filter_by_currency": currency,
        "page_number": 0,
        "units": "metric",
        "checkin_date": checkin_date,
        "locale": locale,
        "order_by": "popularity",
        "latitude": latitude,
        "longitude": longitude,
        "adults_number": adults,
        "checkout_date": checkout_date,
        "include_adjacency": "true"
    }
    if categories_filter_ids:
        params["categories_filter_ids"] = categories_filter_ids
    if children_ages:
        params["children_ages"] = children_ages
    query = urllib.parse.urlencode(params, doseq=True)
    conn.request("GET", f"/v1/hotels/search-by-coordinates?{query}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_hotel_description(hotel_id, locale="en-gb"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({"hotel_id": hotel_id, "locale": locale})
    conn.request("GET", f"/v1/hotels/description?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_room_list(hotel_id, checkin_date, checkout_date, adults_by_rooms, children_by_rooms, children_ages, locale="en-gb", units="metric", currency="AED"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({
        "hotel_id": hotel_id,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "adults_number_by_rooms": adults_by_rooms,
        "children_number_by_rooms": children_by_rooms,
        "children_ages": children_ages,
        "locale": locale,
        "units": units,
        "currency": currency
    })
    conn.request("GET", f"/v2/hotels/room-list?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_search_filters(dest_id, checkin_date, checkout_date, adults=2, children=2, room_number=1, categories_filter_ids=None, children_ages=None, locale="en-gb", currency="AED"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = {
        "categories_filter_ids": categories_filter_ids or "class::2,class::4,free_cancellation::1",
        "page_number": 0,
        "adults_number": adults,
        "children_number": children,
        "dest_id": dest_id,
        "checkin_date": checkin_date,
        "room_number": room_number,
        "order_by": "popularity",
        "include_adjacency": "true",
        "filter_by_currency": currency,
        "units": "metric",
        "children_ages": children_ages or "5,0",
        "checkout_date": checkout_date,
        "dest_type": "city",
        "locale": locale
    }
    query = urllib.parse.urlencode(params, doseq=True)
    conn.request("GET", f"/v2/hotels/search-filters?{query}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def v2_search_hotels(dest_id, checkin_date, checkout_date, adults=2, children=2, room_number=1, categories_filter_ids=None, children_ages=None, locale="en-gb", currency="AED"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = {
        "children_number": children,
        "adults_number": adults,
        "categories_filter_ids": categories_filter_ids or "class::2,class::4,free_cancellation::1",
        "children_ages": children_ages or "5,0",
        "checkout_date": checkout_date,
        "dest_type": "city",
        "page_number": 0,
        "units": "metric",
        "order_by": "popularity",
        "room_number": room_number,
        "checkin_date": checkin_date,
        "filter_by_currency": currency,
        "dest_id": dest_id,
        "locale": locale,
        "include_adjacency": "true"
    }
    query = urllib.parse.urlencode(params, doseq=True)
    conn.request("GET", f"/v2/hotels/search?{query}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_hotel_details(hotel_id, checkin_date, checkout_date, currency="AED", locale="en-gb"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({
        "hotel_id": hotel_id,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "currency": currency,
        "locale": locale
    })
    conn.request("GET", f"/v2/hotels/details?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_calendar_pricing(hotel_id, checkin_date, checkout_date, adults=2, children=2, children_ages="5,0", currency="AED", locale="en-gb"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({
        "hotel_id": hotel_id,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "adults_number": adults,
        "children_number": children,
        "children_ages": children_ages,
        "currency_code": currency,
        "locale": locale
    })
    conn.request("GET", f"/v2/hotels/calendar-pricing?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_hotel_description_v2(hotel_id, locale="en-gb"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({"hotel_id": hotel_id, "locale": locale})
    conn.request("GET", f"/v2/hotels/description?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_hotel_description_full(hotel_id, locale="en-gb"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = urllib.parse.urlencode({"hotel_id": hotel_id, "locale": locale})
    conn.request("GET", f"/v2/hotels/description-full?{params}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def get_meta_properties():
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    conn.request("GET", "/v2/hotels/meta-properties", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def search_hotels_by_coordinates_v2(latitude, longitude, checkin_date, checkout_date, adults=2, children=2, room_number=1, categories_filter_ids=None, children_ages=None, locale="en-gb", currency="AED"):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    params = {
        "include_adjacency": "true",
        "children_ages": children_ages or "5,0",
        "categories_filter_ids": categories_filter_ids or "class::2,class::4,free_cancellation::1",
        "page_number": 0,
        "children_number": children,
        "adults_number": adults,
        "checkout_date": checkout_date,
        "longitude": longitude,
        "room_number": room_number,
        "order_by": "popularity",
        "units": "metric",
        "checkin_date": checkin_date,
        "latitude": latitude,
        "filter_by_currency": currency,
        "locale": locale
    }
    query = urllib.parse.urlencode(params, doseq=True)
    conn.request("GET", f"/v2/hotels/search-by-coordinates?{query}", headers={
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

if __name__ == "__main__":
    # Example usage
    hotels = search_hotels(
        city="New York",
        checkin_date="2025-07-10",
        checkout_date="2025-07-30",
        adults=2,
        children=1
    )
    for hotel in hotels[:3]:
        print(f"Hotel: {hotel.get('hotel_name')}, Address: {hotel.get('address')}, Price: {hotel.get('min_total_price')}, Rating: {hotel.get('review_score')}")
