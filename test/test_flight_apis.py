# This file was moved from the project root to the test/ directory.
# It tests the flight APIs integration.

import requests

kiwi_headers = {
    'x-rapidapi-key': "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738",
    'x-rapidapi-host': "kiwi-com-cheap-flights.p.rapidapi.com"
}

# Kiwi.com One-way
one_way_url = "https://kiwi-com-cheap-flights.p.rapidapi.com/one-way"
one_way_params = {
    'source': 'Country:GB',
    'destination': 'City:dubrovnik_hr',
    'currency': 'usd',
    'locale': 'en',
    'adults': 1,
    'children': 0,
    'infants': 0,
    'handbags': 1,
    'holdbags': 0,
    'cabinClass': 'ECONOMY',
    'sortBy': 'QUALITY',
    'applyMixedClasses': 'true',
    'allowChangeInboundDestination': 'true',
    'allowChangeInboundSource': 'true',
    'allowDifferentStationConnection': 'true',
    'enableSelfTransfer': 'true',
    'allowOvernightStopover': 'true',
    'enableTrueHiddenCity': 'true',
    'allowReturnToDifferentCity': 'false',
    'allowReturnFromDifferentCity': 'false',
    'enableThrowAwayTicketing': 'true',
    'outbound': 'SUNDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY,MONDAY,TUESDAY',
    'transportTypes': 'FLIGHT',
    'contentProviders': 'FLIXBUS_DIRECTS,FRESH,KAYAK,KIWI',
    'limit': 2
}
one_way_resp = requests.get(one_way_url, headers=kiwi_headers, params=one_way_params)
print('Kiwi One Way:', one_way_resp.text)

# Kiwi.com Round-trip
round_trip_url = "https://kiwi-com-cheap-flights.p.rapidapi.com/round-trip"
round_trip_params = one_way_params.copy()
round_trip_params['sortOrder'] = 'ASCENDING'
round_trip_resp = requests.get(round_trip_url, headers=kiwi_headers, params=round_trip_params)
print('Kiwi Round Trip:', round_trip_resp.text)

# Google Flights
google_headers = {
    'x-rapidapi-key': "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738",
    'x-rapidapi-host': "google-flights2.p.rapidapi.com"
}
google_url = "https://google-flights2.p.rapidapi.com/api/v1/searchAirport"
google_params = {'query': 'BER', 'language_code': 'en-US', 'country_code': 'US'}
google_resp = requests.get(google_url, headers=google_headers, params=google_params)
print('Google Flights Search Airport:', google_resp.text)
