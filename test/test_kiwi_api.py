# This file was moved from the project root to the test/ directory.
# It tests the Kiwi flight API integration.

import http.client

headers = {
    'x-rapidapi-key': "f3fddc0b7amshcd1dc2b6f139257p132444jsn7b2183d56738",
    'x-rapidapi-host': "kiwi-com-cheap-flights.p.rapidapi.com"
}

# One-way
conn1 = http.client.HTTPSConnection("kiwi-com-cheap-flights.p.rapidapi.com")
conn1.request("GET", "/one-way?source=Country%3AGB&destination=City%3Adubrovnik_hr&currency=usd&locale=en&adults=1&children=0&infants=0&handbags=1&holdbags=0&cabinClass=ECONOMY&sortBy=QUALITY&applyMixedClasses=true&allowChangeInboundDestination=true&allowChangeInboundSource=true&allowDifferentStationConnection=true&enableSelfTransfer=true&allowOvernightStopover=true&enableTrueHiddenCity=true&allowReturnToDifferentCity=false&allowReturnFromDifferentCity=false&enableThrowAwayTicketing=true&outbound=SUNDAY%2CWEDNESDAY%2CTHURSDAY%2CFRIDAY%2CSATURDAY%2CMONDAY%2CTUESDAY&transportTypes=FLIGHT&contentProviders=FLIXBUS_DIRECTS%2CFRESH%2CKAYAK%2CKIWI&limit=2", headers)
res1 = conn1.getresponse()
data1 = res1.read()
print('One Way:', data1.decode('utf-8'))

# Round-trip
conn2 = http.client.HTTPSConnection("kiwi-com-cheap-flights.p.rapidapi.com")
conn2.request("GET", "/round-trip?source=Country%3AGB&destination=City%3Adubrovnik_hr&currency=usd&locale=en&adults=1&children=0&infants=0&handbags=1&holdbags=0&cabinClass=ECONOMY&sortBy=QUALITY&sortOrder=ASCENDING&applyMixedClasses=true&allowReturnFromDifferentCity=true&allowChangeInboundDestination=true&allowChangeInboundSource=true&allowDifferentStationConnection=true&enableSelfTransfer=true&allowOvernightStopover=true&enableTrueHiddenCity=true&enableThrowAwayTicketing=true&outbound=SUNDAY%2CWEDNESDAY%2CTHURSDAY%2CFRIDAY%2CSATURDAY%2CMONDAY%2CTUESDAY&transportTypes=FLIGHT&contentProviders=FLIXBUS_DIRECTS%2CFRESH%2CKAYAK%2CKIWI&limit=2", headers)
res2 = conn2.getresponse()
data2 = res2.read()
print('Round Trip:', data2.decode('utf-8'))
