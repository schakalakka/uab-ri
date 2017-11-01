from time import sleep

import requests

from meetup.API_KEY import *

cities = [('Barcelona', 'es'), ('Berlin', 'de')]  # list of cities with (city_name, country_code)

max_elems_per_page = 200
offset = 0
params = {'sign': 'true', 'key': API_KEY, 'page': max_elems_per_page, 'offset': offset}




def get_open_events(params):
    r = requests.get("http://api.meetup.com/2/open_events", params=params)
    return r.json()

def get_open_events_of_city(city, country_code):
    params['city'] = city
    params['country'] = country_code
    number_results = max_elems_per_page
    whole_data = []
    offset = -1
    while max_elems_per_page == number_results:
        offset += 1
        params['offset'] = offset
        data = get_open_events(params)
        number_results = data['meta']['count']
        whole_data.extend(data['results'])
        sleep(1)
    return whole_data

def filter_location_for_coordinates(data):
    lat_lon_data = []
    number_events_without_location = 0
    for elem in data:
        if elem.get('venue'):
            lat = elem.get('venue')['lat']
            lon = elem.get('venue')['lon']
            lat_lon_data.append((lat, lon))
        else:
            number_events_without_location += 1
    return lat_lon_data, number_events_without_location


events_per_city={}
number_events_withouts_location_per_city = {}
for city, country_code in cities:
    data, no_events_wo_loc = filter_location_for_coordinates(get_open_events_of_city(city, country_code))
    events_per_city[city] = data
    number_events_withouts_location_per_city[city] = no_events_wo_loc

print(events_per_city)
print(number_events_withouts_location_per_city)
