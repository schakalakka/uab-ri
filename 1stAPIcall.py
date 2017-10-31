# -*- coding: utf-8 -*-

# To install it: pip install meetup.api
from meetup.api import Client


# Defining the API KEY. This belongs to my user: Martí Municoy
API_KEY = "506e773111d2617241037376029726d"
FILE_NAME = "results.txt"

# Initiate a Meet Up client with the API KEY
client = Client(api_key=API_KEY)

# Get a complete list of all the Meet Up activities
categories = client.GetCategories().results

# Some of the cities that I have already tried. The one with the largest amount of activities is London
cities = {"Barcelona": {"city": "Barcelona", "country": "es"},
          "Madrid": {"city": "Madrid", "country": "es"},
          "Middlesbrough": {"city": "Middlesbrough", "country": "gb"},
          "London": {"city": "London", "country": "gb"},
          "Paris": {"city": "Paris", "country": "fr"}}

# Introduce here, the city that you want to analize
city = "Paris"

# A simple function that writes all Meet Up activites found in the chosen city arranged by category
with open(str(city + "_" + FILE_NAME), 'w', encoding="utf-8") as f:
    f.write("LOOKING FOR ALL THE MEET UP EVENTS IN " + str(city).upper() + ":\n\n")
    for category in categories:
        k = 0
        f.write(str(category["name"]) + "\n")
        for i in range(len(category["name"])):
            f.write("-")
        f.write("\n")
        # Get all city's events that match with a specific category
        city_events = client.GetOpenEvents(**cities[city], category=category["id"]).results
        for event in city_events:
            f.write(("\t" + str(event["name"]) + "\n"))
            k += 1
        f.write("\nTotal amount of " + str(category["name"]) + " events: " + repr(k) + "\n\n")
            

"""

cities_coords = {"Barcelona": {"lat": 41.400001525878906, "lon": 2.1700000762939453, "radius": 3}, "Madrid": {"lat": 40.41999816894531, "lon": -3.7100000381469727, "radius": 4}}

city_events = client.GetOpenEvents(**cities_coords["Madrid"])

with open(FILE_NAME, 'w') as f:
    for i, event in enumerate(city_events.results):
        f.write("\nEvent " + repr(i) + "\n")
        f.write(str(event))
        

cities = client.GetCities(country="es")


with open("cities.txt", 'w') as f:
    for i, city in enumerate(cities.results):
        f.write("\nCity " + repr(i) + "\n")
        f.write(str(city))
    print(i)
    

city_events2 = client.GetOpenEvents(country="es", city="barcelona", category=categories["Career & Business"])

with open("results2.txt", 'w') as f:
    for i, event in enumerate(city_events2.results):
        f.write("\nEvent " + repr(i + 1) + "\n")
        f.write(str(event))


cities = client.GetCities(lat=41, lon=2, radius=20)

for city in cities.results:
    write(city["city"] + "\n")
    write(str(city))
"""