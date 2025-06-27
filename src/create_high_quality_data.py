#!/usr/bin/env python3
"""
Targeted Data Augmentation for 80% Accuracy
Focus on improving the specific issues identified in testing
"""
import json
import random
from datetime import datetime, timedelta

def generate_english_flight_examples():
    """Generate high-quality English flight examples with perfect slot extraction"""
    
    cities = [
        "Berlin", "London", "Paris", "Rome", "Madrid", "Barcelona", "Munich", 
        "Hamburg", "Frankfurt", "Vienna", "Zurich", "Amsterdam", "Brussels",
        "Copenhagen", "Oslo", "Stockholm", "Prague", "Warsaw", "Budapest"
    ]
    
    patterns = [
        "Find flights from {origin} to {destination}",
        "I need a flight from {origin} to {destination}",
        "Book a flight from {origin} to {destination}",
        "Search for flights from {origin} to {destination}",
        "Show me flights from {origin} to {destination}",
        "Get me a flight from {origin} to {destination}",
        "Looking for flights from {origin} to {destination}",
        "Find cheap flights from {origin} to {destination}",
        "Any flights from {origin} to {destination}?",
        "Flights from {origin} to {destination} please"
    ]
    
    date_patterns = [
        "",  # No date
        " tomorrow",
        " on July 15",
        " on {date}",
        " from July 1 to July 10",
        " from {start_date} to {end_date}",
        " next week",
        " next month"
    ]
    
    examples = []
    
    for i in range(200):  # Generate 200 examples
        origin = random.choice(cities)
        destination = random.choice([c for c in cities if c != origin])
        pattern = random.choice(patterns)
        date_pattern = random.choice(date_patterns)
        
        # Generate dates
        base_date = datetime(2025, 7, 1)
        start_date = base_date + timedelta(days=random.randint(0, 365))
        end_date = start_date + timedelta(days=random.randint(1, 14))
        
        formatted_start = start_date.strftime("%Y-%m-%d")
        formatted_end = end_date.strftime("%Y-%m-%d")
        
        text = pattern.format(origin=origin, destination=destination)
        
        slots = {
            "origin": origin,
            "destination": destination
        }
        
        if "{date}" in date_pattern:
            text += date_pattern.format(date=formatted_start)
            slots["date"] = formatted_start
        elif "{start_date}" in date_pattern:
            text += date_pattern.format(start_date=formatted_start, end_date=formatted_end)
            slots["start_date"] = formatted_start
            slots["end_date"] = formatted_end
        elif date_pattern:
            text += date_pattern
            if "tomorrow" in date_pattern:
                slots["date"] = "tomorrow"
            elif "next week" in date_pattern:
                slots["date"] = "next week"
            elif "next month" in date_pattern:
                slots["date"] = "next month"
            elif "July" in date_pattern:
                if "to" in date_pattern:
                    slots["start_date"] = "July 1"
                    slots["end_date"] = "July 10"
                else:
                    slots["date"] = "July 15"
        
        examples.append({
            "text": text,
            "intent": "flight_search",
            "slots": slots
        })
    
    return examples

def generate_date_range_examples():
    """Generate examples with complex date ranges"""
    
    cities = ["London", "Paris", "Berlin", "Rome", "Madrid", "Vienna", "Prague"]
    
    patterns = [
        ("What's the weather in {city} from {start} to {end}?", "weather"),
        ("Weather forecast for {city} from {start} to {end}", "weather"),
        ("Book a hotel in {city} from {start} to {end}", "hotel_booking"),
        ("Find hotels in {city} from {start} to {end}", "hotel_search"),
        ("I need accommodation in {city} from {start} to {end}", "hotel_booking")
    ]
    
    date_ranges = [
        ("December 16", "December 23", "2025-12-16", "2025-12-23"),
        ("July 1", "July 10", "2025-07-01", "2025-07-10"),
        ("March 15", "March 20", "2025-03-15", "2025-03-20"),
        ("August 5", "August 10", "2025-08-05", "2025-08-10"),
        ("January 10", "January 15", "2025-01-10", "2025-01-15"),
        ("June 1", "June 7", "2025-06-01", "2025-06-07"),
        ("September 20", "September 25", "2025-09-20", "2025-09-25"),
        ("October 10", "October 15", "2025-10-10", "2025-10-15")
    ]
    
    examples = []
    
    for pattern, intent in patterns:
        for start_str, end_str, start_iso, end_iso in date_ranges:
            for city in cities:
                text = pattern.format(city=city, start=start_str, end=end_str)
                
                slots = {
                    "city": city,
                    "start_date": start_iso,
                    "end_date": end_iso
                }
                
                examples.append({
                    "text": text,
                    "intent": intent,
                    "slots": slots
                })
    
    return examples

def generate_attractions_examples():
    """Generate attraction/park examples to improve intent classification"""
    
    cities = ["Munich", "Berlin", "Vienna", "Paris", "Rome", "Madrid", "London", "Amsterdam"]
    
    patterns = [
        ("Show me parks in {city}", "attractions"),
        ("Find parks in {city}", "attractions"),
        ("What parks are in {city}?", "attractions"),
        ("List attractions in {city}", "attractions"),
        ("Show me attractions in {city}", "attractions"),
        ("What to see in {city}?", "attractions"),
        ("Tourist attractions in {city}", "attractions"),
        ("Best sights in {city}", "attractions"),
        ("Museums in {city}", "attractions"),
        ("Things to do in {city}", "attractions"),
        ("Sightseeing in {city}", "attractions"),
        ("Places to visit in {city}", "attractions"),
        # German versions
        ("Zeig mir Parks in {city}", "attractions"),
        ("Parks in {city}", "attractions"),
        ("Sehenswürdigkeiten in {city}", "attractions"),
        ("Was kann man in {city} sehen?", "attractions"),
        ("Attraktionen in {city}", "attractions"),
        ("Museen in {city}", "attractions")
    ]
    
    examples = []
    
    for pattern, intent in patterns:
        for city in cities:
            text = pattern.format(city=city)
            
            slots = {
                "city": city
            }
            
            examples.append({
                "text": text,
                "intent": intent,
                "slots": slots
            })
    
    return examples

def generate_weather_city_examples():
    """Generate weather examples with better city extraction"""
    
    cities = ["London", "Berlin", "Paris", "Rome", "Madrid", "Vienna", "Munich", "Hamburg"]
    
    patterns = [
        ("What's the weather in {city}?", "weather"),
        ("Weather in {city}", "weather"),
        ("How's the weather in {city}?", "weather"),
        ("Current weather in {city}", "weather"),
        ("Weather forecast for {city}", "weather"),
        ("Tell me the weather in {city}", "weather"),
        ("Is it raining in {city}?", "weather"),
        ("Temperature in {city}", "weather"),
        # German versions
        ("Wie ist das Wetter in {city}?", "weather"),
        ("Wetter in {city}", "weather"),
        ("Wettervorhersage für {city}", "weather"),
        ("Temperatur in {city}", "weather"),
        ("Regnet es in {city}?", "weather")
    ]
    
    examples = []
    
    for pattern, intent in patterns:
        for city in cities:
            text = pattern.format(city=city)
            
            slots = {
                "city": city
            }
            
            examples.append({
                "text": text,
                "intent": intent,
                "slots": slots
            })
    
    return examples

def generate_hotel_examples():
    """Generate hotel examples with better slot extraction"""
    
    cities = ["Paris", "Berlin", "Munich", "Vienna", "Rome", "Madrid", "London"]
    
    patterns = [
        ("Book a hotel in {city} for 2 adults and 1 child", "hotel_booking"),
        ("Find hotels in {city} for 2 adults", "hotel_search"),
        ("I need a hotel in {city}", "hotel_booking"),
        ("Hotels in {city} for families", "hotel_search"),
        ("Accommodation in {city}", "hotel_search"),
        ("Book accommodation in {city}", "hotel_booking"),
        # German versions
        ("Buche ein Hotel in {city} für 2 Erwachsene", "hotel_booking"),
        ("Hotel in {city} für 2 Erwachsene und 1 Kind", "hotel_booking"),
        ("Brauche ein Hotel in {city}", "hotel_booking"),
        ("Hotels in {city}", "hotel_search")
    ]
    
    examples = []
    
    for pattern, intent in patterns:
        for city in cities:
            text = pattern.format(city=city)
            
            slots = {
                "city": city
            }
            
            # Add adults/children info for some patterns
            if "2 adults" in text or "2 Erwachsene" in text:
                slots["adults"] = 2
            if "1 child" in text or "1 Kind" in text:
                slots["children"] = 1
            
            examples.append({
                "text": text,
                "intent": intent,
                "slots": slots
            })
    
    return examples

def create_high_quality_dataset():
    """Create a high-quality dataset focused on problematic areas"""
    
    print("🎯 Generating targeted training examples...")
    
    all_examples = []
    
    # Generate different types of examples
    all_examples.extend(generate_english_flight_examples())
    print(f"  ✈️  Generated {len(generate_english_flight_examples())} flight examples")
    
    date_examples = generate_date_range_examples()
    all_examples.extend(date_examples)
    print(f"  📅 Generated {len(date_examples)} date range examples")
    
    attraction_examples = generate_attractions_examples()
    all_examples.extend(attraction_examples)
    print(f"  🏛️  Generated {len(attraction_examples)} attraction examples")
    
    weather_examples = generate_weather_city_examples()
    all_examples.extend(weather_examples)
    print(f"  🌤️  Generated {len(weather_examples)} weather examples")
    
    hotel_examples = generate_hotel_examples()
    all_examples.extend(hotel_examples)
    print(f"  🏨 Generated {len(hotel_examples)} hotel examples")
    
    # Shuffle examples
    random.shuffle(all_examples)
    
    # Write to file
    output_file = 'data/high_quality_training_data.jsonl'
    print(f"\n💾 Writing {len(all_examples)} examples to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ High-quality dataset created: {len(all_examples)} examples")
    
    # Print statistics
    intent_counts = {}
    slot_counts = {}
    
    for example in all_examples:
        intent = example.get('intent')
        if intent:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        for slot_key in example.get('slots', {}).keys():
            slot_counts[slot_key] = slot_counts.get(slot_key, 0) + 1
    
    print("\n📊 Intent distribution:")
    for intent, count in sorted(intent_counts.items()):
        print(f"  {intent}: {count}")
    
    print("\n🏷️  Slot distribution:")
    for slot, count in sorted(slot_counts.items()):
        print(f"  {slot}: {count}")
    
    return all_examples

if __name__ == "__main__":
    print("🚀 Creating high-quality training data for 80% accuracy...")
    examples = create_high_quality_dataset()
    print("\n🎉 High-quality dataset creation completed!")
