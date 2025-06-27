"""
collect_data.py
Collects travel arguments and weather/flight/accommodation data from all sources for model training.
"""
import json
from src.data_extraction import booking_scraper, tripadvisor_scraper, openweathermap_fetcher, flightapi_fetcher

# Example URLs (replace/add more for real data)
booking_urls = [
    "https://www.booking.com/articles/en-gb/tips-for-travelling-with-pets.html"
]
tripadvisor_urls = [
    "https://www.tripadvisor.com/Travel-g191-c18213/United-States:Tips.For.Traveling.With.Pets.html"
]
cities = ["London", "Berlin", "Tokyo"]

# Collect Booking.com arguments
booking_args = []
for url in booking_urls:
    args = booking_scraper.fetch_booking_article(url)
    for a in args:
        booking_args.append({"source": url, "text": a, "type": "booking"})

# Collect TripAdvisor arguments
tripadvisor_args = []
for url in tripadvisor_urls:
    args = tripadvisor_scraper.fetch_tripadvisor_article(url)
    for a in args:
        tripadvisor_args.append({"source": url, "text": a, "type": "tripadvisor"})

# Collect weather data
weather_data = []
for city in cities:
    weather = openweathermap_fetcher.fetch_weather_data(location=city)
    weather_data.append({"city": city, "weather": weather, "type": "weather"})

# Collect flight data (example: London to Berlin)
flight_data = []
flight = flightapi_fetcher.fetch_flight_data(origin="LON", destination="BER", date="2025-07-01")
flight_data.append({"origin": "LON", "destination": "BER", "date": "2025-07-01", "flight": flight, "type": "flight"})

# Save all data
all_data = booking_args + tripadvisor_args + weather_data + flight_data
with open("data/collected_travel_data.json", "w") as f:
    json.dump(all_data, f, indent=2)
print("Data collection complete. Saved to data/collected_travel_data.json")
