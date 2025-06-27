"""
Gradio Conversational Travel Advice Chatbot
- Accepts free-form user questions
- Extracts intent (topic, city, date, etc.) using OpenAI (if available)
- Calls your data pipeline for weather, flights, accommodations, etc.
- Remembers previous answers and avoids repetition
"""
import gradio as gr
import re
import datetime
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_extraction import openweathermap_fetcher, flightapi_fetcher
from data_extraction.booking_api import (
    search_hotels, get_exchange_rates, get_children_policies, search_hotels_by_coordinates, get_hotel_description
)
from assistant.functionImplementation import get_hotels_api_v2
from src.argument_classifier import nli
import dateutil.parser
from deep_translator import GoogleTranslator
from data_extraction.flight_apis import kiwi_one_way, kiwi_round_trip, google_flights_request
from data_extraction.tripadvisor_search import search_tripadvisor
from data_extraction.travel_advisor_api import get_travel_advice

# Set OpenAI API key
import openai
openai.api_key = "sk-abcdef1234567890abcdef1234567890abcdef12"
USE_OPENAI = True

# Load trained classifier for demo
import pickle
try:
    with open("data/travel_classifier.pkl", "rb") as f:
        vectorizer, clf = pickle.load(f)
    USE_CLASSIFIER = True
except Exception:
    USE_CLASSIFIER = False

# Simple regex-based fallback for weather queries
def parse_weather_query(text):
    # Improved city extraction: look for 'in <city>' or before 'from' if present
    city = None
    city_match = re.search(r'in ([A-Za-z ]+?)(?: from|$|\?)', text)
    if city_match:
        city = city_match.group(1).strip()
    else:
        # Try to extract city before 'from' if present
        city_match2 = re.search(r'weather in ([A-Za-z ]+?)(?: from|$|\?)', text, re.IGNORECASE)
        if city_match2:
            city = city_match2.group(1).strip()
        else:
            # Fallback: look for 'weather in <city>'
            city_match3 = re.search(r'weather in ([A-Za-z ]+)', text, re.IGNORECASE)
            if city_match3:
                city = city_match3.group(1).strip()
    # Date range extraction (improved: only match if 'from ... to ...' is present)
    date_match = re.search(r'from ([A-Za-z0-9 .,-]+) to ([A-Za-z0-9 .,-]+?)(?: in|$|\?)', text)
    if not date_match:
        # Try to match date range like 'from 23. to 27.12.2024'
        date_match = re.search(r'from ([0-9]{1,2})[. ]*to ([0-9]{1,2})[. ]*([0-9]{1,2})[. ]*([0-9]{4})', text)
        if date_match:
            # e.g. from 23. to 27.12.2024
            start_day = date_match.group(1)
            end_day = date_match.group(2)
            end_month = date_match.group(3)
            end_year = date_match.group(4)
            start = f"{end_month} {start_day} {end_year}"
            end = f"{end_month} {end_day} {end_year}"
            def parse_date_simple(date_str):
                try:
                    dt = datetime.datetime.strptime(date_str, "%m %d %Y")
                    return dt.date().isoformat(), {'year': dt.year, 'month': dt.month}
                except Exception:
                    return date_str, None
            start_date, context = parse_date_simple(start)
            end_date, _ = parse_date_simple(end)
            return city, start_date, end_date
    # Date range extraction
    date_match = re.search(r'from ([A-Za-z0-9 .,-]+) to ([A-Za-z0-9 .,-]+?)(?: in|$|\?)', text)
    def parse_date(date_str, context=None, force_year=None, force_month=None):
        date_str = re.sub(r' in .+$', '', date_str).strip()
        fmts = ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%B %d", "%b %d", "%d %B", "%d %b", "%d, %Y"]
        for fmt in fmts:
            try:
                # If the format does not include a year, append the context or default year (2025)
                if '%Y' not in fmt and not re.search(r'\d{4}', date_str):
                    year = force_year or (context['year'] if context and 'year' in context else 2025)
                    date_str_with_year = f"{date_str}, {year}"
                    dt = datetime.datetime.strptime(date_str_with_year, fmt + ", %Y")
                else:
                    dt = datetime.datetime.strptime(date_str, fmt)
                # If year is missing, use force_year/context/2025
                if dt.year == 1900:
                    if force_year:
                        dt = dt.replace(year=force_year)
                    elif context and 'year' in context:
                        dt = dt.replace(year=context['year'])
                    else:
                        dt = dt.replace(year=2025)
                if force_month:
                    dt = dt.replace(month=force_month)
                return dt.date().isoformat(), {'year': dt.year, 'month': dt.month}
            except Exception:
                continue
        # Try to extract just the day if present (for end date like '23')
        day_match = re.match(r'^(\d{1,2})$', date_str)
        if day_match and context:
            day = int(day_match.group(1))
            year = context['year'] if context and 'year' in context else (force_year if force_year else 2025)
            month = context['month'] if context and 'month' in context else (force_month if force_month else 1)
            return f"{year}-{month:02d}-{day:02d}", {'year': year, 'month': month}
        # Try to extract day and month (e.g., '10 August')
        day_month_match = re.match(r'^(\d{1,2})[\s-]+([A-Za-z]+)$', date_str)
        if day_month_match:
            day = int(day_month_match.group(1))
            month_str = day_month_match.group(2)
            try:
                month = datetime.datetime.strptime(month_str, "%B").month
            except ValueError:
                try:
                    month = datetime.datetime.strptime(month_str, "%b").month
                except ValueError:
                    month = context['month'] if context and 'month' in context else 1
            year = context['year'] if context and 'year' in context else (force_year if force_year else 2025)
            return f"{year}-{month:02d}-{day:02d}", {'year': year, 'month': month}
        # Try to extract just the year if present
        year_match = re.search(r'(\d{4})', date_str)
        if year_match and context:
            return f"{context['year']}-{context['month']:02d}-{int(date_str.split(',')[0]):02d}", {'year': context['year'], 'month': context['month']}
        return date_str.strip(), context
    if date_match:
        start = date_match.group(1).strip()
        end = date_match.group(2).strip()
        # Helper to check if a date string contains a month name
        def has_month(date_str):
            months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
                      "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
            return any(m in date_str.lower() for m in months)
        # Parse end date first to get context
        end_date_tmp, end_context = parse_date(end)
        # Only inherit month/year for start if it doesn't have a month
        if has_month(start):
            start_date, start_context = parse_date(start)
        else:
            start_date, start_context = parse_date(start, context=end_context, force_year=end_context['year'] if end_context and 'year' in end_context else 2025, force_month=end_context['month'] if end_context and 'month' in end_context else None)
        # Always inherit for end date if missing
        end_date, _ = parse_date(end, context=start_context, force_year=start_context['year'] if start_context and 'year' in start_context else 2025, force_month=start_context['month'] if start_context and 'month' in start_context else None)
    else:
        start_date = end_date = None
    return city, start_date, end_date

def get_weather_advice(city, start_date, end_date):
    if not city:
        return "Please specify a city for weather information."
    
    # Handle single date case
    if start_date and not end_date:
        end_date = start_date
    
    # If both start and end date are present, try to fetch daily weather for the range
    if start_date and end_date and start_date != end_date:
        try:
            # Try to fetch daily weather for each date in the range
            start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            days = min((end_dt - start_dt).days + 1, 7)  # Limit to 7 days
            results = []
            for i in range(days):
                day = start_dt + datetime.timedelta(days=i)
                # Use OpenWeatherMap for current/historical/forecast
                weather = openweathermap_fetcher.fetch_weather_data(location=city)
                if 'weather' in weather and 'main' in weather:
                    desc = weather['weather'][0]['description']
                    temp_max = weather['main'].get('temp_max', weather['main'].get('temp', ''))
                    temp_min = weather['main'].get('temp_min', weather['main'].get('temp', ''))
                    results.append(f"{day.strftime('%B %d, %Y')}: {desc}, Max {temp_max}°C, Min {temp_min}°C")
                else:
                    results.append(f"{day.strftime('%B %d, %Y')}: Weather data unavailable.")
            return "<br>".join(results)
        except Exception as e:
            return f"Error fetching weather range: {e}"
    
    # Single date or current weather
    elif start_date:
        try:
            weather = openweathermap_fetcher.fetch_weather_data(location=city)
            if 'weather' in weather and 'main' in weather:
                desc = weather['weather'][0]['description']
                temp_max = weather['main'].get('temp_max', weather['main'].get('temp', ''))
                temp_min = weather['main'].get('temp_min', weather['main'].get('temp', ''))
                return f"{start_date}: {desc}, Max {temp_max}°C, Min {temp_min}°C"
            else:
                return f"Weather data unavailable for {city} on {start_date}."
        except Exception as e:
            return f"Error fetching weather: {e}"
    
    # If no date range, fetch current weather
    try:
        weather = openweathermap_fetcher.fetch_weather_data(location=city)
        if 'weather' in weather and 'main' in weather:
            desc = weather['weather'][0]['description']
            temp = weather['main']['temp']
            return f"Current weather in {city}: {desc}, {temp}°C"
        else:
            return f"Could not fetch current weather for {city}."
    except Exception as e:
        return f"Error fetching current weather: {e}"

def parse_flight_query(text):
    # Extract origin, destination, and date range for flight queries
    # e.g. 'flight from berlin to London from 23. to 27.12.2024'
    match = re.search(r'flight from ([A-Za-z ]+) to ([A-Za-z ]+)[^\d]*(from [^\n]+)', text, re.IGNORECASE)
    if match:
        origin = match.group(1).strip().title()
        destination = match.group(2).strip().title()
        date_part = match.group(3)
        _, start_date, end_date = parse_weather_query(date_part)
        return origin, destination, start_date, end_date
    return None, None, None, None

def city_to_iata(city):
    if not city:
        return None
    mapping = {
        'berlin': 'BER',
        'london': 'LON',
        'munich': 'MUC',
        'frankfurt': 'FRA',
        'paris': 'PAR',
        'rome': 'ROM',
        'madrid': 'MAD',
        'vienna': 'VIE',
        'zurich': 'ZRH',
        'amsterdam': 'AMS',
        'dubai': 'DXB',
        'istanbul': 'IST',
        'new york': 'NYC',
        'los angeles': 'LAX',
        'tokyo': 'TYO',
        'singapore': 'SIN',
        'bangkok': 'BKK',
        'barcelona': 'BCN',
        'prague': 'PRG',
        'budapest': 'BUD',
        'warsaw': 'WAW',
        'helsinki': 'HEL',
        'copenhagen': 'CPH',
        'stockholm': 'STO',
        'oslo': 'OSL',
        'brussels': 'BRU',
        'manchester': 'MAN',
        'dublin': 'DUB',
        'athens': 'ATH',
        'lisbon': 'LIS',
        'venice': 'VCE',
        'milan': 'MIL',
        'geneva': 'GVA',
        'nice': 'NCE',
        'hamburg': 'HAM',
        'stuttgart': 'STR',
        'duesseldorf': 'DUS',
        'cologne': 'CGN',
        'palma': 'PMI',
        'mallorca': 'PMI',
        'dubrovnik': 'DBV',
        'split': 'SPU',
        'zagreb': 'ZAG',
        'sofia': 'SOF',
        'bucharest': 'BUH',
        'krakow': 'KRK',
        'gdansk': 'GDN',
        'poznan': 'POZ',
        'wroclaw': 'WRO',
        'riga': 'RIX',
        'vilnius': 'VNO',
        'tallinn': 'TLL',
        'moscow': 'MOW',
        'saint petersburg': 'LED',
        'kyiv': 'IEV',
        'lviv': 'LWO',
        'odessa': 'ODS',
        'minsk': 'MSQ',
        'beijing': 'BJS',
        'shanghai': 'SHA',
        'hong kong': 'HKG',
        'delhi': 'DEL',
        'mumbai': 'BOM',
        'bangalore': 'BLR',
        'sydney': 'SYD',
        'melbourne': 'MEL',
        'auckland': 'AKL',
        'cape town': 'CPT',
        'johannesburg': 'JNB',
        'cairo': 'CAI',
        'tel aviv': 'TLV',
        'doha': 'DOH',
        'riyadh': 'RUH',
        'jeddah': 'JED',
        'toronto': 'YTO',
        'montreal': 'YMQ',
        'vancouver': 'YVR',
        'miami': 'MIA',
        'san francisco': 'SFO',
        'chicago': 'CHI',
        'washington': 'WAS',
        'boston': 'BOS',
        'seattle': 'SEA',
        'houston': 'HOU',
        'dallas': 'DFW',
        'atlanta': 'ATL',
        'orlando': 'MCO',
        'las vegas': 'LAS',
        'philadelphia': 'PHL',
        'detroit': 'DTT',
        'minneapolis': 'MSP',
        'denver': 'DEN',
        'phoenix': 'PHX',
        'san diego': 'SAN',
        'montreal': 'YMQ',
        'calgary': 'YYC',
        'edmonton': 'YEG',
        'ottawa': 'YOW',
        'winnipeg': 'YWG',
        'halifax': 'YHZ',
        'quebec': 'YQB',
        'victoria': 'YYJ',
        'regina': 'YQR',
        'saskatoon': 'YXE',
        'st johns': 'YYT',
        'charlottetown': 'YYG',
        'fredericton': 'YFC',
        'moncton': 'YQM',
        'saint john': 'YSJ',
        'thunder bay': 'YQT',
        'whitehorse': 'YXY',
        'yellowknife': 'YZF',
        'iqaluit': 'YFB',
    }
    return mapping.get(city.lower().strip(), city.upper().strip())

def get_flight_advice(origin, destination, start_date, end_date, adults=1, children=0, infants=0, use_kiwi=False, use_google=True):
    """
    Fetch flight info using Google Flights via RapidAPI only.
    """
    if not origin or not destination:
        return "Please specify both origin and destination for flight search."
    
    if not start_date:
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date().isoformat()
        start_date = tomorrow
    
    origin_code = city_to_iata(origin)
    destination_code = city_to_iata(destination)
    
    if not origin_code or not destination_code:
        return f"Could not find airport codes for {origin} or {destination}."
    
    results = []
    errors = []
    if use_google:
        try:
            google_params = {
                'departure_id': origin_code,
                'arrival_id': destination_code,
                'outbound_date': start_date,
            }
            if end_date and end_date != start_date:
                google_params['return_date'] = end_date
            google_result = google_flights_request('/api/v1/searchFlights', google_params)
            # Pretty print Google Flights results
            import json
            try:
                data = json.loads(google_result)
                if data.get('status') and 'data' in data and 'itineraries' in data['data'] and 'topFlights' in data['data']['itineraries']:
                    flights = data['data']['itineraries']['topFlights']
                    pretty = []
                    for f in flights:
                        dep = f['flights'][0]['departure_airport']['airport_name']
                        arr = f['flights'][0]['arrival_airport']['airport_name']
                        dep_time = f['flights'][0]['departure_airport']['time']
                        arr_time = f['flights'][0]['arrival_airport']['time']
                        airline = f['flights'][0]['airline']
                        flight_num = f['flights'][0]['flight_number']
                        price = f.get('price', 'N/A')
                        pretty.append(f"{airline} {flight_num}: {dep} ({dep_time}) → {arr} ({arr_time}), Price: {price}")
                    results.append("<b>Google Flights Results:</b><br>" + "<br>".join(pretty))
                else:
                    results.append(f"<b>Google Flights Results (raw):</b><br>{google_result[:2000]}")
            except Exception:
                results.append(f"<b>Google Flights Results (raw):</b><br>{google_result[:2000]}")
        except Exception as e:
            errors.append(f"Google Flights error: {e}")
    if not results:
        return '<br>'.join(errors) if errors else 'No flight data found.'
    return '<br><br>'.join(results)

def get_hotel_advice(city, start_date, end_date, num_adults=1, num_children=0, location=None, breakfast=False):
    print(f"DEBUG: get_hotel_advice called with city={city}, start_date={start_date}, end_date={end_date}, num_adults={num_adults}, num_children={num_children}")
    """
    Real hotel search using Booking.com API via RapidAPI, with extra info.
    """
    # Handle missing dates
    if not start_date:
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date().isoformat()
        start_date = tomorrow
    if not end_date:
        end_date = start_date
    
    try:
        hotels = search_hotels(city, start_date, end_date, adults=num_adults, children=num_children)
        if not hotels:
            # Try with alternative city names
            alternative_cities = {
                'paris': ['Paris', 'Paris, France'],
                'rome': ['Rome', 'Roma', 'Rome, Italy'],
                'berlin': ['Berlin', 'Berlin, Germany'],
                'munich': ['Munich', 'München', 'Munich, Germany'],
                'vienna': ['Vienna', 'Wien', 'Vienna, Austria'],
                'zurich': ['Zurich', 'Zürich', 'Zurich, Switzerland']
            }
            
            city_lower = city.lower() if city else ''
            if city_lower in alternative_cities:
                for alt_city in alternative_cities[city_lower]:
                    hotels = search_hotels(alt_city, start_date, end_date, adults=num_adults, children=num_children)
                    if hotels:
                        break
            
            if not hotels:
                return f"No hotels found for '{city}' for the given dates."
        hotel = hotels[0]
        name = hotel.get('hotel_name', 'Unknown')
        address = hotel.get('address', 'N/A')
        price = hotel.get('min_total_price', 'N/A')
        rating = hotel.get('review_score', 'N/A')
        url = hotel.get('url', '#')
        hotel_id = hotel.get('hotel_id')
        # Get hotel description
        description = ""
        if hotel_id:
            try:
                desc_data = get_hotel_description(hotel_id)
                description = desc_data.get('description', '')
            except Exception:
                pass
        # Get children policy
        children_policy = ""
        if hotel_id and num_children > 0:
            try:
                policy_data = get_children_policies(hotel_id, children_age=5)
                children_policy = policy_data.get('children_policies', '')
            except Exception:
                pass
        return (
            f"🏨 <b>{name}</b> ({rating}/10)<br>"
            f"Address: {address}<br>"
            f"Price: <b>{price} EUR</b> for your stay<br>"
            f"{description}<br>"
            f"Children policy: {children_policy}<br>"
            f"<a href='{url}'>View on Booking.com</a>"
        )
    except Exception as e:
        return f"Error fetching hotel data: {e}"

def get_hotel_advice_v2(city, start_date, end_date, num_adults=2, num_children=0, rooms=1, locale="en-gb", currency="AED"):
    """
    Hotel search using Booking.com API v2 endpoints (RapidAPI).
    """
    return get_hotels_api_v2(city, start_date, end_date, adults=num_adults, children=num_children, rooms=rooms, locale=locale, currency=currency)

# Chatbot state: store previous Q&A
chat_history = {}

import subprocess

def extract_intent_and_slots(text):
    # Call intent model
    intent = None
    try:
        result = subprocess.run([
            "python3", "src/infer_intent_slot.py", text
        ], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.startswith("Intent:"):
                intent = line.split(":", 1)[1].strip()
    except Exception:
        intent = None
    # Call slot NER model
    slots = {}
    try:
        result = subprocess.run([
            "python3", "src/infer_slot_ner.py", text
        ], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.startswith("Slots:"):
                slots = eval(line.split(":", 1)[1].strip())
    except Exception:
        slots = {}
    return intent, slots

def normalize_dates_from_slots(slots, text=None):
    import re
    def try_parse(date_str, ref_year=None, ref_month=None):
        try:
            # Fix for 'from 23' or similar patterns
            if isinstance(date_str, str) and date_str.strip().startswith('from '):
                date_str = date_str.strip().replace('from ', '')
            # If year is missing, use ref_year or 2025
            if ref_year and not any(y in date_str for y in ["2024", "2025", "2026"]):
                if ref_month and re.match(r'^\d{1,2}\\.?$', date_str.strip()):
                    # Only day provided, use ref_month and ref_year
                    date_str = f"{ref_year}-{ref_month:02d}-{int(date_str.strip('. ')):02d}"
                else:
                    date_str = f"{date_str}.{ref_year}"
            dt = dateutil.parser.parse(date_str, dayfirst=True, fuzzy=True, default=None)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None
    ref_year = None
    ref_month = None
    if text:
        m = re.search(r'(20\d{2})', text)
        if m:
            ref_year = int(m.group(1))
        m2 = re.search(r'(1[0-2]|0?[1-9])[.\-/ ]+20\d{2}', text)
        if m2:
            ref_month = int(m2.group(1))
    # If end_date is a full date, extract its year/month for start_date
    end_date_raw = slots.get("end_date")
    end_year = end_month = None
    if end_date_raw:
        try:
            dt = dateutil.parser.parse(end_date_raw, dayfirst=True, fuzzy=True, default=None)
            end_year = dt.year
            end_month = dt.month
        except Exception:
            pass
    for k in ["start_date", "end_date", "date"]:
        if k in slots and slots[k]:
            if k == "start_date" and end_year and end_month and re.match(r'^\d{1,2}\\.?$', slots[k].strip()):
                slots[k] = try_parse(slots[k], end_year, end_month)
            else:
                slots[k] = try_parse(slots[k], ref_year, ref_month)
    return slots

def translate_to_english(text):
    return GoogleTranslator(source='de', target='en').translate(text)

def parse_german_month(date_str):
    months = {
        'januar': 'January', 'februar': 'February', 'märz': 'March', 'april': 'April', 'mai': 'May', 'juni': 'June',
        'juli': 'July', 'august': 'August', 'september': 'September', 'oktober': 'October', 'november': 'November', 'dezember': 'December',
        'jan': 'Jan', 'feb': 'Feb', 'mär': 'Mar', 'apr': 'Apr', 'jun': 'Jun', 'jul': 'Jul', 'aug': 'Aug', 'sep': 'Sep', 'okt': 'Oct', 'nov': 'Nov', 'dez': 'Dec'
    }
    for de, en in months.items():
        if de in date_str.lower():
            return date_str.lower().replace(de, en)
    return date_str

def chat_fn(message, history):
    # Translate German to English if detected (simple check for German keywords)
    if re.search(r"\b(Berlin|Juli|Flug|Hotel|Frühstück|Kind|Erwachsene|zwischen|und|nach|von|mit|inklusive|benötige|möchte|Rückflug|Nähe|Parks)\b", message, re.IGNORECASE):
        message_en = translate_to_english(message)
    else:
        message_en = message
    # Check if we've already answered this
    if message in chat_history:
        return chat_history[message]
    # Use deep learning models for intent and slot extraction
    intent, slots = extract_intent_and_slots(message_en)
    slots = normalize_dates_from_slots(slots, message_en)
    # Patch German month names in slots
    for k in ["start_date", "end_date", "date"]:
        if k in slots and slots[k]:
            slots[k] = parse_german_month(slots[k])
    # Extract all relevant slots
    origin = slots.get("origin")
    destination = slots.get("destination")
    start_date = slots.get("start_date") or slots.get("date")
    end_date = slots.get("end_date")
    stopover = slots.get("stopover") or slots.get("via")
    city = slots.get("city") or destination
    hotel_location = slots.get("park") or slots.get("location")
    
    # Regex fallback for origin/destination if not found by NER
    if intent and "flight" in intent and (not origin or not destination):
        # Clean and specific patterns for English
        # Pattern 1: "flights from X to Y"
        flight_pattern1 = re.search(r'\bflights?\s+from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message_en, re.IGNORECASE)
        if flight_pattern1:
            if not origin:
                origin = flight_pattern1.group(1).strip()
            if not destination:
                destination = flight_pattern1.group(2).strip()
        
        # Pattern 2: "from X to Y" (more general)
        elif not origin or not destination:
            from_to_pattern = re.search(r'\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message_en, re.IGNORECASE)
            if from_to_pattern:
                if not origin:
                    origin = from_to_pattern.group(1).strip()
                if not destination:
                    destination = from_to_pattern.group(2).strip()
        
        # Pattern 3: "X to Y" (simple)
        elif not origin or not destination:
            simple_to_pattern = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message_en, re.IGNORECASE)
            if simple_to_pattern and not re.search(r'\b(want|need|like|prefer|going)\s+to\b', message_en, re.IGNORECASE):
                if not origin:
                    origin = simple_to_pattern.group(1).strip()
                if not destination:
                    destination = simple_to_pattern.group(2).strip()
        
        # German pattern: "von X nach Y" (already working well)
        german_match = re.search(r'\bvon\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+nach\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message, re.IGNORECASE)
        if german_match:
            if not origin:
                origin = german_match.group(1).strip()
            if not destination:
                destination = german_match.group(2).strip()
    
    # Additional fallback for weather queries if city not found
    if intent and "weather" in intent and not city:
        # Try to extract city from "weather in X" pattern
        weather_match = re.search(r'\b(?:weather|wetter)\s+(?:in|für)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message_en, re.IGNORECASE)
        if weather_match:
            city = weather_match.group(1).strip()
        # German pattern
        german_weather = re.search(r'\b(?:wetter|temperatur)\s+(?:in|für)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message, re.IGNORECASE)
        if german_weather:
            city = german_weather.group(1).strip()
    
    # Hotel city extraction fallback
    if intent and "hotel" in intent and not city:
        # Try to extract city from "hotel in X" pattern
        hotel_match = re.search(r'\b(?:hotel|accommodation)\s+(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message_en, re.IGNORECASE)
        if hotel_match:
            city = hotel_match.group(1).strip()
        # German pattern
        german_hotel = re.search(r'\b(?:hotel|unterkunft)\s+(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message, re.IGNORECASE)
        if german_hotel:
            city = german_hotel.group(1).strip()
    
    # Improved date range extraction for queries like "from Dec 16 to 23"
    if not start_date or not end_date:
        # Pattern: "from Month Day to Day, Year"
        date_range_pattern1 = re.search(r'\bfrom\s+([A-Z][a-z]+\s+\d{1,2})\s+to\s+(\d{1,2}),?\s*(\d{4})?', message_en, re.IGNORECASE)
        if date_range_pattern1:
            start_part = date_range_pattern1.group(1)  # "December 16"
            end_day = date_range_pattern1.group(2)     # "23"
            year = date_range_pattern1.group(3) or "2025"
            
            # Extract month from start_part
            month_match = re.search(r'([A-Z][a-z]+)', start_part, re.IGNORECASE)
            if month_match:
                month = month_match.group(1)
                start_date = f"{start_part}, {year}"
                end_date = f"{month} {end_day}, {year}"
        
        # Pattern: "vom X. bis Y. Month" (German)
        elif not start_date or not end_date:
            german_date_pattern = re.search(r'\bvom\s+(\d{1,2})\.\s+bis\s+(\d{1,2})\.\s+([A-Z][a-z]+)', message, re.IGNORECASE)
            if german_date_pattern:
                start_day = german_date_pattern.group(1)
                end_day = german_date_pattern.group(2)
                month = german_date_pattern.group(3)
                start_date = f"{start_day}. {month}"
                end_date = f"{end_day}. {month}"
    # Try to extract number of adults/children from message (simple regex)
    num_adults = 2 if re.search(r"zwei Erwachsene|2 Erwachsene|2 adult", message, re.IGNORECASE) else 1
    num_children = 1 if re.search(r"ein Kind|1 Kind|1 child", message, re.IGNORECASE) else 0
    breakfast = bool(re.search(r"frühstück|breakfast", message, re.IGNORECASE))
    # Slot normalization: if only 'date' is present, use for both start_date and end_date
    if not start_date and 'date' in slots:
        start_date = end_date = slots['date']
    if not start_date and not end_date and 'date' in slots:
        start_date = end_date = slots['date']
    # Fallback: if no date is extracted, check for 'tomorrow' or 'today' in the message
    if not start_date:
        if re.search(r'\btomorrow\b', message, re.IGNORECASE):
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date().isoformat()
            start_date = end_date = tomorrow
        elif re.search(r'\btoday\b', message, re.IGNORECASE):
            today = datetime.datetime.now().date().isoformat()
            start_date = end_date = today
    # If only one of start_date or end_date is present, treat as single-date query
    if start_date and not end_date:
        end_date = start_date
    if end_date and not start_date:
        start_date = end_date
    # If only city is present and intent is flight, try to infer origin/destination
    if intent == 'flight' and not origin and not destination and 'city' in slots:
        # Use regex fallback or context to assign city to origin/destination
        pass
    
    # Override intent for specific keywords
    if re.search(r'\b(parks?|attractions?|sights?|museums?|sightsee|sehenswürdigkeiten|parks|museen)\b', message, re.IGNORECASE):
        intent = 'attractions'
    
    # DEBUG: Print extracted slots and key variables
    print(f"DEBUG: intent={intent}, slots={slots}")
    print(f"DEBUG: origin={origin}, destination={destination}, start_date={start_date}, end_date={end_date}")
    # Build response from API results only
    response = ""
    if intent and "weather" in intent:
        weather_info = get_weather_advice(city, start_date, end_date)
        response += f"\n\nWeather Info: {weather_info}"
    elif intent and "flight" in intent:
        flight_info = get_flight_advice(origin, destination, start_date, end_date, num_adults, num_children)
        response += f"\n\nFlight Info: {flight_info}"
    elif intent and ("hotel" in intent or "accommodation" in intent):
        hotel_info = get_hotel_advice(city, start_date, end_date, num_adults, num_children)
        response += f"\n\nHotel Info: {hotel_info}"
    elif intent and "attractions" in intent:
        response += f"\n\nAttractions in {city}:"
    # Add TripAdvisor travel advice
    travel_advice = get_travel_advice(message)
    if travel_advice and 'No TripAdvisor results found.' not in travel_advice:
        response += f"\n\n{travel_advice}"
    return response.strip() or "Sorry, I couldn't find any travel information for your request."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--test_tripadvisor":
        from data_extraction.travel_advisor_api import get_travel_advice
        query = sys.argv[2]
        print("Travel Advisor API result:\n")
        print(get_travel_advice(query))
        sys.exit(0)
    # Launch Gradio ChatInterface
    gr.ChatInterface(chat_fn, title="Conversational Travel Assistant", description="Ask about travel, weather, flights, hotels, and get up-to-date TripAdvisor advice.").launch()
