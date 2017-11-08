from time import sleep
import csv
import requests
import sys

max_elems_per_page = 200
offset = 0
params = {'sign': 'true', 'page': max_elems_per_page, 'offset': offset}


def add_key(mu_key):
    """
    Add key to the MeetUp's parameter dictionary

    Parameters
    ----------
    mu_key : string
        This is the MeetUp API key
    """
    params['key'] = mu_key


def get_open_events():
    """
    This function makes a request to the MeetUp API in order to obtain open
    events according to the parameters previously defined in params dictionary.
    In case that something goes wrong when reading the request answer during
    the json translation, the function calls itself in order to try to get
    the requested data again.
    These error readings are usually detected in this process but, after
    several attempts, the function is able to get the right data from MeetUp.

    Returns
    -------
    json : JSON formatted list
        This JSON formated list contains information of the requested events.
    """
    r = requests.get("http://api.meetup.com/2/open_events", params=params)
    try:
        json = r.json()
        if 'code' in json:
            print(" Client throttled, use another key or try it again later")
            sys.exit(0)
        return json
    except Exception:
        print(" Reading error, trying again")
        return get_open_events()


def get_categories():
    """
    This function makes a request to the MeetUp API in order to obtain a list
    of the available categories for all the MeetUp activities.
    In case that something goes wrong when reading the request answer during
    the json translation, the function calls itself in order to try to get
    the requested data again.
    These error readings are not detected in this process very often but, after
    several attempts, the function is able to get the right data from MeetUp.

    Returns
    -------
    json : JSON formatted list
        This JSON formated list contains all the available categories.

    """
    categories = []
    r = requests.get("http://api.meetup.com/2/categories", params=params)
    try:
        json = r.json()
        if 'code' in json:
            print(" Client throttled, use another key or try it again later")
            sys.exit(0)
        categories.extend(json['results'])
        return categories
    except Exception:
        print(" Reading error, trying again")
        return get_categories()


def get_open_events_of_city(city, code_list, category=None):
    """
    It returns a list of all the available MeetUp events in a city.

    Arguments
    ---------
    city : string
        Name of the city where we want to perform the search
    code_list : either string or list of strings
        It is a string that contains the country code where the city belongs
        to. In case of cities from United States, a state code is also
        mandatory. Then, code_list is defined as a list of strings made up of
        the country code and the state code.
    category : integer
        It is the id that defines a MeetUp category. If it is given, the
        functino will only return events related with this category. If it is
        not given, the function will return all the events without filtering
        by their category.

    Returns
    -------
    results : JSON formatted list
        It includes information about the events found in a city.
    """
    params['city'] = city
    if type(code_list) is tuple:
        params['country'] = code_list[0]
        params['state'] = code_list[1]
    else:
        params['country'] = code_list
    if category is not None:
        params['category'] = category
    number_results = max_elems_per_page
    results = []
    offset = -1
    while max_elems_per_page <= number_results:
        offset += 1
        params['offset'] = offset
        data = get_open_events()
        try:
            number_results = data['meta']['count']
            results.extend(data['results'])
        except KeyError:
            print(data)
        # To avoid throttling the client
        sleep(1)
    return results


def filter_location_for_coordinates(data):
    """
    It filters all the events according to their location. Events with lon/lat
    equal to 0/0 will be removed.

    Parameters
    ----------
    data : JSON formatted list
        It includes general information about some events.

    Returns
    -------
    lat_lon_data : list of coordinate tuples
        It consists on the latitude and longitude coordinates of each activity
        from the input.
    number_events_without_location : integer
        Number of events with lon/lat equal to 0/0 that were filtered.
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


def write_num_activities(city, num_activities, f=None):
    """
    It writes down the total number of activities that were found in a city to
    an output csv file.

    Parameters
    ----------
    city : string
        Name of the city.
    num_activities : integer
        Total number of activities that were found in that city.
    f : file object
        This is the object belonging to the file that was opened. If it is not
        given, a file will be opened according to the city name.
    """
    if f is None:
        with open('{}.csv'.format(city), 'w') as f:
            f.write("#0\n{}\n!#\n".format(num_activities))
    else:
        f.write("#0\n{}\n!#\n".format(num_activities))


def write_locations(city, locations, f=None, category_id=None):
    """
    It writes down the locations for each one of the activities that were found
    in a city to an output csv file.

    Parameters
    ----------
    city : string
        Name of the city.
    locations : list of coordinate tuples
        It consists on the latitude and longitude coordinates of each activity
        found.
    f : file object
        This is the object belonging to the file that was opened. If it is not
        given, a file will be opened according to the city name.
    category_id : integer
        It is the category id where all the activities from the locations data
        belong to. If it is not given, no information about the category will
        be written.
    """
    if f is None:
        with open('{}.csv'.format(city), 'w') as f:
            csvwriter = csv.writer(f, delimiter=';')
            if category_id is not None:
                f.write("#{}\n".format(category_id))
            csvwriter.writerows(locations)
            if category_id is not None:
                f.write("!#\n")
    else:
        csvwriter = csv.writer(f, delimiter=';')
        if category_id is not None:
            f.write("#{}\n".format(category_id))
        csvwriter.writerows(locations)
        if category_id is not None:
            f.write("!#\n")
