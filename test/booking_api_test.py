from data_extraction.booking_api import search_hotels, get_hotel_description, get_children_policies, get_exchange_rates

if __name__ == "__main__":
    # Debug/test Booking.com API hotel search for multiple cities
    test_cities = ["New York", "Berlin", "London", "Paris", "Tokyo"]
    checkin_date = "2025-07-10"
    checkout_date = "2025-07-15"
    adults = 2
    children = 1
    for city in test_cities:
        print(f"\nSearching hotels in {city} from {checkin_date} to {checkout_date} for {adults} adults and {children} child...")
        hotels = search_hotels(city, checkin_date, checkout_date, adults=adults, children=children)
        print(f"Found {len(hotels)} hotels in {city}.")
        for hotel in hotels[:3]:
            print(f"Hotel: {hotel.get('hotel_name')}, Address: {hotel.get('address')}, Price: {hotel.get('min_total_price')}, Rating: {hotel.get('review_score')}, ID: {hotel.get('hotel_id')}")
        if hotels:
            hotel_id = hotels[0].get('hotel_id')
            print(f"\nTesting hotel description for hotel_id={hotel_id}...")
            desc = get_hotel_description(hotel_id)
            print(desc)
            print(f"\nTesting children policies for hotel_id={hotel_id}...")
            policy = get_children_policies(hotel_id, children_age=5)
            print(policy)
    print("\nTesting exchange rates...")
    rates = get_exchange_rates(currency="USD")
    print(rates)
