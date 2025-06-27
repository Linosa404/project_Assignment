from data_extraction.booking_api import (
    get_room_list, get_search_filters, v2_search_hotels, get_hotel_details, get_calendar_pricing, get_hotel_description_v2, get_hotel_description_full, get_meta_properties, search_hotels_by_coordinates_v2
)

if __name__ == "__main__":
    print("\nTesting /v2/hotels/room-list...")
    print(get_room_list(
        hotel_id="1676161",
        checkin_date="2025-10-14",
        checkout_date="2025-10-15",
        adults_by_rooms="3,1",
        children_by_rooms="2,1",
        children_ages="5,0,9"
    ))

    print("\nTesting /v2/hotels/search-filters...")
    print(get_search_filters(
        dest_id="-553173",
        checkin_date="2025-10-14",
        checkout_date="2025-10-15"
    ))

    print("\nTesting /v2/hotels/search...")
    print(v2_search_hotels(
        dest_id="-553173",
        checkin_date="2025-10-14",
        checkout_date="2025-10-15"
    ))

    print("\nTesting /v2/hotels/details...")
    print(get_hotel_details(
        hotel_id="1676161",
        checkin_date="2025-10-14",
        checkout_date="2025-10-15"
    ))

    print("\nTesting /v2/hotels/calendar-pricing...")
    print(get_calendar_pricing(
        hotel_id="1377073",
        checkin_date="2025-10-14",
        checkout_date="2025-10-15"
    ))

    print("\nTesting /v2/hotels/description...")
    print(get_hotel_description_v2(
        hotel_id="1377073"
    ))

    print("\nTesting /v2/hotels/description-full...")
    print(get_hotel_description_full(
        hotel_id="1377073"
    ))

    print("\nTesting /v2/hotels/meta-properties...")
    print(get_meta_properties())

    print("\nTesting /v2/hotels/search-by-coordinates...")
    print(search_hotels_by_coordinates_v2(
        latitude="65.9667",
        longitude="-18.5333",
        checkin_date="2025-10-14",
        checkout_date="2025-10-15"
    ))
