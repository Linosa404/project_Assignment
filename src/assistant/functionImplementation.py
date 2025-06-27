import os
import random
import re
import smtplib
import time
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import http.client
import urllib.parse
import json

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ics import Calendar, Event

load_dotenv()

# Retrieve the API key for Visual Crossing from environment variables
api_key = os.getenv("VISUAL_CROSSING_API_KEY")

def get_current_date():
    """
    Retrieve the current date in the format 'YYYY-MM-DD'.
    """
    return datetime.now().strftime("%Y-%m-%d")

def get_weather_forecast(location, start_date, end_date):
    """
    Fetch weather forecast for a specified location and date range.
    Uses the Visual Crossing API to retrieve weather data.
    """
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    url = f"{base_url}/{location}/{start_date}/{end_date}?unitGroup=metric&include=days&key={api_key}&contentType=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather_summary = []
        for day in data.get("days", []):
            day_summary = {
                "date": day.get("datetime"),
                "temp_max": day.get("tempmax"),
                "temp_min": day.get("tempmin"),
                "conditions": day.get("conditions")
            }
            weather_summary.append(day_summary)

        result = "\n".join(
            f"Date: {day['date']}, Max Temp: {day['temp_max']}°C, "
            f"Min Temp: {day['temp_min']}°C, Conditions: {day['conditions']}"
            for day in weather_summary
        )
        return result

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching weather data: {e}")
        return None

def get_flights(departure, arrival, persons, outbound_date, return_date):
    """
    Retrieve flight information for a specific route and date range.
    Scrapes data from Swoodoo, handling retries for robustness.
    """
    max_retries = 10
    delay = 3

    base_url = "https://www.swoodoo.com/flights"
    if persons == 1:
        url = f"{base_url}/{departure}-{arrival}/{outbound_date}/{return_date}?ucs=3ccv3e&sort=price_a"
    else:
        url = f"{base_url}/{departure}-{arrival}/{outbound_date}/{return_date}/{persons}adults?ucs=3ccv3e&sort=price_a"

    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            preise = soup.find_all("div", class_="f8F1-price-text")
            flugdauer = soup.find_all("div", class_="vmXl vmXl-mod-variant-large")
            operatoren = soup.find_all("div", class_="J0g6-operator-text")
            stops = soup.find_all("span", class_="JWEO-stops-text")

            if preise and operatoren and flugdauer and stops:
                fluege_strings = []

                for i, (price, operator) in enumerate(zip(preise, operatoren)):
                    durations = flugdauer[i*2:i*2+2]
                    stops_values = stops[i*2:i*2+2]

                    flug_string = (
                        f"Price: {price.text.strip()} | "
                        f"Operator: {operator.text.strip()} | "
                        f"Flight duration and stops: "
                        f"({durations[0].text.strip()} - {stops_values[0].text.strip()}), "
                        f"({durations[1].text.strip()} - {stops_values[1].text.strip()})"
                    )

                    fluege_strings.append(flug_string)

                final_output = "\n".join(fluege_strings)
                return final_output

            print(f"Keine Daten gefunden, versuche erneut... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
            delay = random.randint(1, 5)
        else:
            print(f"Kaputt weil: HTTP {response.status_code}, versuche erneut... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
            delay = random.randint(1, 5)

    return "Es gibt keine Flüge."

def get_hotels(city, checkin_date, checkout_date, adults, rooms):
    """
    Retrieve hotel information for a specified city and date range.
    Scrapes data from Booking.com to provide hotel details.
    """
    url = build_booking_url(city, checkin_date, checkout_date, adults, rooms)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        hotel_divs = soup.find_all("div", {"data-testid": "property-card"}, limit=5)

        if hotel_divs:
            hotel_strings = []
            for i, hotel in enumerate(hotel_divs, start=1):
                name = hotel.find("div", {"data-testid": "title"})
                hotel_name = name.text.strip() if name else "Kein Name gefunden"

                price = hotel.find("span", {"data-testid": "price-and-discounted-price", "aria-hidden": "true"})
                hotel_price = price.text.strip() if price else "Kein Preis gefunden"

                rating = hotel.find("span", {"data-testid": "review-score", "aria-hidden": "true"})
                hotel_rating = rating.text.strip() if rating else "Keine Bewertung gefunden"

                distance = hotel.find("span", {"data-testid": "distance"})
                hotel_distance = distance.text.strip() if distance else "Keine Entfernung gefunden"

                info = hotel.find("div", {"data-testid": "recommended-units"})
                hotel_info = info.text.strip() if info else "Keine Info gefunden"
                formatted_hotel_info = re.sub(
                    r"(?<=[a-z])(?=[A-Z])|(?<=[0-9])(?=[A-Z])|(?<=[m²])(?=[0-9])|(?<=\))(?=[A-Z])|(?<=[a-z])(?=\d)",
                    ", ",
                    hotel_info
                )

                hotel_string = (
                    f"Hotel {i}:  | "
                    f"  Name: {hotel_name} | "
                    f"  Preis: {hotel_price} | "
                    f"  Rating: {hotel_rating} | "
                    f"  Entfernung: {hotel_distance} | "
                    f"  Hotel info: {formatted_hotel_info} | "
                )

                hotel_strings.append(hotel_string)

            final_output = "\n".join(hotel_strings)
            return final_output
        else:
            return print("Keine Hotels gefunden.")
    else:
       return print("Kaputt weil:", response.status_code)

def build_booking_url(city, checkin_date, checkout_date, adults, rooms=1, lang="de"):
    """
    Construct a URL for Booking.com with specified search parameters.
    """
    base_url = "https://www.booking.com/searchresults.de.html"
    params = {
        "ss": city,
        "checkin": checkin_date,
        "checkout": checkout_date,
        "group_adults": adults,
        "no_rooms": rooms,
        "lang": lang,
    }
    param_string = "&".join(f"{key}={value}" for key, value in params.items())
    print(f"{base_url}?{param_string}")
    return f"{base_url}?{param_string}"

def create_calendar_event(event_details):
    """
    Create a calendar event in ICS format based on provided event details.
    """
    try:
        cal = Calendar()
        event = Event()
        event.name = event_details.get("title", "No Title")
        event.begin = event_details["start"]
        event.end = event_details["end"]
        event.location = event_details.get("location", "")
        event.description = event_details.get("description", "")
        cal.events.add(event)

        return str(cal)

    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None

def send_email_with_calendar(recipient, subject, body, calendar_event_details):
    """
    Send an email with an attached calendar event in ICS format.
    Uses SMTP to send the email.
    """
    try:
        ics_file = create_calendar_event(calendar_event_details)
        if not ics_file:
            print("Failed to create calendar event. Email not sent.")
            return "Failed to send email."

        smtp_server = "mail.komtur.org"
        smtp_port = 587
        sender = "reiseinfo@komtur.org"
        sender_password = "reiseinfo"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        part = MIMEBase('text', 'calendar')
        part.set_payload(ics_file)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="event.ics"')
        msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, sender_password)
            server.send_message(msg)
            print("Email sent successfully with calendar event.")

    except Exception as e:
        print(f"An error occurred: {e}")

def get_hotels_api_v2(city, checkin_date, checkout_date, adults=2, children=0, rooms=1, locale="en-gb", currency="AED"):
    """
    Retrieve hotel information using Booking.com API v2 endpoints (via RapidAPI).
    Returns a string summary of the top hotels found.
    """
    from data_extraction import booking_api
    # Step 1: Get destination id for the city
    conn = http.client.HTTPSConnection(booking_api.RAPIDAPI_HOST)
    params = urllib.parse.urlencode({"name": city, "locale": locale})
    conn.request("GET", f"/v1/hotels/locations?{params}", headers={
        'x-rapidapi-key': booking_api.RAPIDAPI_KEY,
        'x-rapidapi-host': booking_api.RAPIDAPI_HOST
    })
    res = conn.getresponse()
    data = res.read()
    locations = json.loads(data.decode("utf-8"))
    if not locations or not isinstance(locations, list) or not locations[0].get('dest_id'):
        return "No destination found for the specified city."
    dest_id = locations[0]["dest_id"]

    # Step 2: Search hotels using v2 endpoint
    hotels_response = booking_api.v2_search_hotels(
        dest_id=dest_id,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        adults=adults,
        children=children,
        room_number=rooms,
        locale=locale,
        currency=currency
    )
    hotels = hotels_response.get("results", [])
    if not hotels:
        return "No hotels found."
    hotel_strings = []
    for i, hotel in enumerate(hotels[:5], start=1):
        name = hotel.get("hotel_name", "No name")
        price = hotel.get("min_total_price", "No price")
        rating = hotel.get("review_score", "No rating")
        address = hotel.get("address", "No address")
        hotel_strings.append(f"Hotel {i}: {name} | Price: {price} | Rating: {rating} | Address: {address}")
    return "\n".join(hotel_strings)