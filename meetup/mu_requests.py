from time import sleep
import csv
import requests

from meetup.API_KEY import *

cities = [('London', 'gb'), ('Barcelona', 'es'), ('Berlin', 'de'), ('Paris', 'fr'), ('Madrid', 'es'), ('Hamburg', 'de'),
          ('New York', ('us', 'NY'))]  # list of cities with (city_name, country_code)

max_elems_per_page = 200
offset = 0
params = {'sign': 'true', 'key': API_KEY, 'page': max_elems_per_page, 'offset': offset}


def get_open_events(params):
    r = requests.get("http://api.meetup.com/2/open_events", params=params)
    return r.json()


def get_open_events_of_city(city, country_code):
    params['city'] = city
    if type(country_code) is tuple:
        params['country'] = country_code[0]
        params['state'] = country_code[1]
    else:
        params['country'] = country_code
    number_results = max_elems_per_page
    results = []
    offset = -1
    while max_elems_per_page - 4 <= number_results:
        offset += 1
        params['offset'] = offset
        data = get_open_events(params)
        number_results = data['meta']['count']
        results.extend(data['results'])
        sleep(1)
    return results


def filter_location_for_coordinates(data):
    """
    filters all the events for location
    events with lon/lat = 0/0 will be removed
    :param data:
    :return: list of coordinate tuples and number of events without location
    """
    lat_lon_data = []
    number_events_without_location = 0
    for elem in data:
        if elem.get('venue'):
            lat = elem.get('venue')['lat']
            lon = elem.get('venue')['lon']
            # filter (0,0) locations
            if lat == lon == 0:
                continue
            lat_lon_data.append((lat, lon))
        else:
            number_events_without_location += 1
    return lat_lon_data, number_events_without_location


def write_locations(city, locations, category=''):
    with open('{}{}.csv'.format(city, category), 'w') as f:
        csvwriter = csv.writer(f, delimiter=';')
        csvwriter.writerows(locations)


events_per_city = {}
number_events_withouts_location_per_city = {}
for city, country_code in cities:
    data, no_events_wo_loc = filter_location_for_coordinates(get_open_events_of_city(city, country_code))
    events_per_city[city] = data
    write_locations(city, data)
    number_events_withouts_location_per_city[city] = (no_events_wo_loc, len(data))

# write_all_locations(events_per_city)

print(events_per_city)
print(number_events_withouts_location_per_city)
