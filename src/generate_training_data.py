#!/usr/bin/env python3
"""
Data augmentation script to improve slot extraction accuracy
Focus areas: English queries, date ranges, city extraction
"""

import json
import itertools

def generate_english_flight_data():
    """Generate comprehensive English flight query training data"""
    
    origins = ["Berlin", "London", "Paris", "Rome", "Madrid", "Barcelona", "Munich", "Hamburg", "Frankfurt", "Vienna", "Zurich", "Amsterdam", "Brussels"]
    destinations = ["Rome", "Paris", "London", "Berlin", "Madrid", "Vienna", "Munich", "Barcelona", "Zurich", "Amsterdam", "Frankfurt", "Hamburg"]
    
    # Flight query templates
    templates = [
        "Find flights from {origin} to {destination}",
        "Book a flight from {origin} to {destination}",
        "I need a flight from {origin} to {destination}",
        "Search flights from {origin} to {destination}",
        "Show me flights from {origin} to {destination}",
        "Get flights from {origin} to {destination}",
        "Flight tickets from {origin} to {destination}",
        "Flights {origin} to {destination}",
        "I want to fly from {origin} to {destination}",
        "Looking for flights from {origin} to {destination}",
    ]
    
    data = []
    
    # Generate combinations
    city_pairs = [(o, d) for o in origins for d in destinations if o != d][:50]  # Limit to 50 pairs
    
    for template in templates:
        for origin, destination in city_pairs[:10]:  # Limit for manageability
            text = template.format(origin=origin, destination=destination)
            data.append({
                "text": text,
                "slots": [
                    {"slot": "origin", "value": origin},
                    {"slot": "destination", "value": destination}
                ]
            })
    
    return data

def generate_date_range_data():
    """Generate date range training data"""
    
    data = []
    
    # English date patterns
    date_templates = [
        "from July 1 to July 10",
        "from December 16 to 23, 2025",
        "July 1 to July 10",
        "from March 5 to March 12",
        "from April 1st to 5th",
        "May 10 to May 15",
        "from June 20 to June 25",
        "August 3 to August 8",
        "from September 12 to 18",
        "October 1 to 7",
        "from November 25 to November 30",
        "January 15 to January 20",
    ]
    
    for template in date_templates:
        # Extract start and end dates
        if "to" in template:
            parts = template.replace("from ", "").split(" to ")
            if len(parts) == 2:
                start_date = parts[0].strip()
                end_date = parts[1].strip()
                
                data.append({
                    "text": template,
                    "slots": [
                        {"slot": "start_date", "value": start_date},
                        {"slot": "end_date", "value": end_date}
                    ]
                })
    
    # German date patterns
    german_dates = [
        "vom 1. Juli bis 10. Juli",
        "vom 16. bis 23. Dezember 2025",
        "vom 5. bis 12. März",
        "vom 1. bis 5. April",
        "vom 10. bis 15. Mai",
        "vom 20. bis 25. Juni",
        "vom 3. bis 8. August",
        "vom 12. bis 18. September",
        "vom 1. bis 7. Oktober",
        "vom 25. bis 30. November",
    ]
    
    for template in german_dates:
        data.append({
            "text": template,
            "slots": [
                {"slot": "start_date", "value": template.split(" bis ")[0].replace("vom ", "")},
                {"slot": "end_date", "value": template.split(" bis ")[1]}
            ]
        })
    
    return data

def generate_weather_city_data():
    """Generate weather query data with proper city extraction"""
    
    cities = ["London", "Paris", "Berlin", "Rome", "Madrid", "Munich", "Hamburg", "Vienna", "Zurich", "Barcelona"]
    
    templates = [
        "What's the weather in {city}",
        "Weather in {city}",
        "How's the weather in {city}",
        "Show me weather for {city}",
        "Weather forecast for {city}",
        "What's the temperature in {city}",
        "Weather conditions in {city}",
        "Is it raining in {city}",
        "Climate in {city}",
        "Weather report for {city}",
    ]
    
    german_templates = [
        "Wie ist das Wetter in {city}",
        "Wetter in {city}",
        "Wettervorhersage für {city}",
        "Wie ist die Temperatur in {city}",
        "Wetterbericht für {city}",
        "Regnet es in {city}",
        "Klima in {city}",
    ]
    
    data = []
    
    for template in templates:
        for city in cities:
            text = template.format(city=city)
            data.append({
                "text": text,
                "slots": [{"slot": "city", "value": city}]
            })
    
    for template in german_templates:
        for city in cities:
            text = template.format(city=city)
            data.append({
                "text": text,
                "slots": [{"slot": "city", "value": city}]
            })
    
    return data

def generate_hotel_data():
    """Generate hotel booking data"""
    
    cities = ["Paris", "Rome", "Berlin", "Munich", "Vienna", "London", "Madrid", "Barcelona", "Amsterdam", "Zurich"]
    
    templates = [
        "Book a hotel in {city}",
        "Find hotels in {city}",
        "I need a hotel in {city}",
        "Hotel in {city}",
        "Accommodation in {city}",
        "Stay in {city}",
        "Where to stay in {city}",
        "Hotels near {city}",
        "Booking hotel in {city}",
        "Reserve hotel in {city}",
    ]
    
    german_templates = [
        "Buche ein Hotel in {city}",
        "Hotel in {city}",
        "Ich brauche ein Hotel in {city}",
        "Unterkunft in {city}",
        "Übernachtung in {city}",
        "Hotels in {city}",
        "Wo übernachten in {city}",
    ]
    
    data = []
    
    for template in templates:
        for city in cities:
            text = template.format(city=city)
            data.append({
                "text": text,
                "slots": [{"slot": "city", "value": city}]
            })
    
    for template in german_templates:
        for city in cities:
            text = template.format(city=city)
            data.append({
                "text": text,
                "slots": [{"slot": "city", "value": city}]
            })
    
    return data

def generate_intent_data():
    """Generate intent classification training data"""
    
    data = []
    
    # Weather intents
    weather_queries = [
        "What's the weather like?",
        "How's the weather?",
        "Weather forecast",
        "Is it raining?",
        "Temperature today",
        "Climate information",
        "Weather conditions",
        "Wie ist das Wetter?",
        "Wettervorhersage",
        "Temperatur",
        "Regnet es?",
    ]
    
    for query in weather_queries:
        data.append({"text": query, "intent": "weather"})
    
    # Flight intents
    flight_queries = [
        "Book flights",
        "Flight tickets",
        "I need a flight",
        "Flight search",
        "Airline tickets",
        "Flying to",
        "Flight booking",
        "Flug buchen",
        "Flugtickets",
        "Ich brauche einen Flug",
        "Flugsuch",
    ]
    
    for query in flight_queries:
        data.append({"text": query, "intent": "flight_search"})
    
    # Hotel intents
    hotel_queries = [
        "Book hotel",
        "Hotel reservation",
        "I need accommodation",
        "Hotel booking",
        "Where to stay",
        "Hotels",
        "Hotel buchen",
        "Hotelreservierung",
        "Ich brauche eine Unterkunft",
        "Übernachtung",
    ]
    
    for query in hotel_queries:
        data.append({"text": query, "intent": "hotel_booking"})
    
    # Attractions intents
    attraction_queries = [
        "Show me parks",
        "Tourist attractions",
        "What to see",
        "Museums",
        "Sightseeing",
        "Places to visit",
        "Attractions",
        "Parks and recreation",
        "Zeig mir Parks",
        "Sehenswürdigkeiten",
        "Was kann man sehen",
        "Museen",
        "Touristenattraktionen",
    ]
    
    for query in attraction_queries:
        data.append({"text": query, "intent": "attractions"})
    
    return data

def combine_flight_with_dates():
    """Generate complex flight queries with dates"""
    
    origins = ["Berlin", "London", "Paris", "Rome", "Munich"]
    destinations = ["Rome", "Paris", "London", "Berlin", "Vienna"]
    
    date_patterns = [
        "from July 1 to July 10",
        "on August 15",
        "from December 16 to 23, 2025",
        "July 1 to July 10",
        "on September 20",
    ]
    
    german_dates = [
        "vom 1. Juli bis 10. Juli", 
        "am 15. August",
        "vom 16. bis 23. Dezember 2025",
    ]
    
    data = []
    
    # English combinations
    for origin in origins[:3]:
        for destination in destinations[:3]:
            if origin != destination:
                for date_pattern in date_patterns[:3]:
                    text = f"Find flights from {origin} to {destination} {date_pattern}"
                    
                    slots = [
                        {"slot": "origin", "value": origin},
                        {"slot": "destination", "value": destination}
                    ]
                    
                    # Add date slots
                    if "from" in date_pattern and "to" in date_pattern:
                        parts = date_pattern.replace("from ", "").split(" to ")
                        if len(parts) == 2:
                            slots.append({"slot": "start_date", "value": parts[0].strip()})
                            slots.append({"slot": "end_date", "value": parts[1].strip()})
                    elif "on" in date_pattern:
                        date_val = date_pattern.replace("on ", "")
                        slots.append({"slot": "date", "value": date_val})
                    
                    data.append({"text": text, "slots": slots})
    
    # German combinations
    for origin in origins[:2]:
        for destination in destinations[:2]:
            if origin != destination:
                for date_pattern in german_dates[:2]:
                    text = f"Finde Flüge von {origin} nach {destination} {date_pattern}"
                    
                    slots = [
                        {"slot": "origin", "value": origin},
                        {"slot": "destination", "value": destination}
                    ]
                    
                    if "vom" in date_pattern and "bis" in date_pattern:
                        parts = date_pattern.replace("vom ", "").split(" bis ")
                        if len(parts) == 2:
                            slots.append({"slot": "start_date", "value": parts[0].strip()})
                            slots.append({"slot": "end_date", "value": parts[1].strip()})
                    elif "am" in date_pattern:
                        date_val = date_pattern.replace("am ", "")
                        slots.append({"slot": "date", "value": date_val})
                    
                    data.append({"text": text, "slots": slots})
    
    return data

def main():
    """Generate all training data and save to files"""
    
    print("Generating enhanced training data...")
    
    # Generate all data categories
    flight_data = generate_english_flight_data()
    date_data = generate_date_range_data()
    weather_data = generate_weather_city_data()
    hotel_data = generate_hotel_data()
    intent_data = generate_intent_data()
    complex_flight_data = combine_flight_with_dates()
    
    # Combine slot data
    slot_ner_data = flight_data + date_data + weather_data + hotel_data + complex_flight_data
    
    # Save slot NER data
    with open("data/enhanced_slot_ner_dataset.jsonl", "w") as f:
        for item in slot_ner_data:
            f.write(json.dumps(item) + "\n")
    
    # Save intent data
    with open("data/enhanced_intent_dataset.jsonl", "w") as f:
        for item in intent_data:
            f.write(json.dumps(item) + "\n")
    
    print(f"Generated {len(slot_ner_data)} slot NER examples")
    print(f"Generated {len(intent_data)} intent examples")
    print("Files saved:")
    print("- data/enhanced_slot_ner_dataset.jsonl")
    print("- data/enhanced_intent_dataset.jsonl")
    
    # Show sample outputs
    print("\nSample slot NER data:")
    for item in slot_ner_data[:5]:
        print(f"  {item}")
    
    print("\nSample intent data:")
    for item in intent_data[:5]:
        print(f"  {item}")

if __name__ == "__main__":
    main()
