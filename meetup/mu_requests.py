from time import sleep
import requests
import sys
import os
from .cities import cities
from .categories import categories as local_categories

max_elems_per_page = 200
params = {'sign': 'true', 'page': max_elems_per_page}


def add_key(mu_key):
    """
    Add key to the MeetUp's parameter dictionary

    Parameters
    ----------
    mu_key : string
        This is the MeetUp API key
    """
    params['key'] = mu_key


def restore_meetup_params():
    """
    """
    global params
    mu_key = params["key"]
    params = {'sign': 'true', 'page': max_elems_per_page, 'key': mu_key}


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
            if "key" in params:
                print(" Client throttled, " +
                      "use another key or try it again later")
            else:
                print("MeetUp key required. Add it by calling add_key() " +
                      "function")
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
            if "key" in params:
                print(" Client throttled, " +
                      "use another key or try it again later")
            else:
                print("MeetUp key required. Add it by calling add_key() " +
                      "function")
            sys.exit(0)
        categories.extend(json['results'])
        return categories
    except Exception:
        print(" Reading error, trying again")
        return get_categories()


def get_open_events_of_city(city, code_list, category_id=None):
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
    category_id : integer
        It is the id that defines a MeetUp category. If it is given, the
        functino will only return events related with this category. If it is
        not given, the function will return all the events without filtering
        by their category.

    Returns
    -------
    results : JSON formatted list
        It includes information about the events found in a city.
    """
    # Defining initial parameters to call MeetUp API
    params['city'] = city
    if type(code_list) is tuple:
        params['country'] = code_list[0]
        params['state'] = code_list[1]
    else:
        params['country'] = code_list
    if category_id is not None:
        params['category'] = category_id

    # Declaring some initial variable before the loop
    number_results = max_elems_per_page
    results = []
    offset = 0

    # Entering into the loop to retrieve all events in the city
    while (number_results != 0):
        params['offset'] = offset
        data = get_open_events()
        number_results = data['meta']['count']
        results.extend(data['results'])
        offset += 1

        # To avoid throttling the client
        sleep(1)

    # The parameters dictionary must be restored to its initial state
    restore_meetup_params()

    return results


def data_parser(data, write_date, write_name, write_id):
    """
    It parses the JSON formatted data in a custom format containing only the
    required data.

    Parameters
    ----------
    data : JSON formatted list
        It includes general information about some events.
    write_date : boolean
        When set to true, it will write down the information about the event
        dates to the csv file.
    write_name : boolean
        When set to true, it will write down the name for each event to the csv
        file.
    write_id : boolean
        When set to true, it will write down the id for each event to the csv
        file.

    Returns
    -------
    parsed_events : list of dictionaries
        Parent list contains different events. Dictionaries contain the parsed
        data with the following format:
            keys:   ["coordinates", "date", "name", "event_id"]
            values: [2-dim tuple of floats, integer, string, string]
    """
    parsed_events = []
    for event in data:
        # Initial values
        event_coordinates = (None, None)
        event_date = None
        event_name = None
        event_id = None
        parsed_data = {}

        # Retrieving latitude and longitude if possible
        if event.get("venue"):
            event_coordinates = (event.get("venue")["lat"],
                                 event.get("venue")["lon"])
            if event_coordinates is (0, 0):
                event_coordinates = (None, None)

        # Retrieving date
        if write_date:
            event_date = event.get("time")

        # Retrieving description
        if write_name:
            event_name = event.get("name")
            # Remove semicolons, they would produce interpretation errors when
            # read from file
            event_name = event_name.replace(';', '')

        if write_id:
            event_id = event.get("id")

        # Save data
        parsed_data["coordinates"] = event_coordinates
        parsed_data["date"] = event_date
        parsed_data["name"] = event_name
        parsed_data["id"] = event_id
        parsed_events.append(parsed_data)

    return parsed_events


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


def name_parser(string):
    """
    It avoids conflicting characters such as line breaks to be printed to the
    file.

    Parameters
    ----------
    string : string
        String to be parsed

    Returns
    -------
    string : string
        Parsed string
    """
    return string.replace('\n', ' ')


def write_data(city, parsed_data, category_id, f):
    """
    It writes down the parsed data for each one of the activities that were
    found in a city to an output csv file.

    Parameters
    ----------
    city : string
        Name of the city.
    parsed_data : list of coordinate tuples
        It consists on the latitude and longitude coordinates of each activity
        found.
    category_id : integer
        It is the category id where all the activities from the locations data
        belong to. If it is not given, no information about the category will
        be written.
    f : file object
        This is the object belonging to the file that was opened.
    parsed_data : list of dictionaries
        Parent list contains different events. Dictionaries contain the parsed
        data with the following format:
            keys:   ["coordinates", "date", "name", "event_id"]
            values: [2-dim tuple of floats, integer, string, string]
    """
    f.write("#{}\n".format(category_id))
    for event in parsed_data:
        parsed_name = name_parser(event["name"])
        f.write("{};{};{};{};{}\n".format(event["coordinates"][0],
                                          event["coordinates"][1],
                                          event["date"], parsed_name,
                                          event["id"]))
    f.write("!#\n")


def categories_parser(categories):
    """
    It creates a dictionary by parsing the JSON format coming from the MeetUp
    Client.

    Parameters
    ----------
    categories : JSON formatted list
        This JSON formated list contains all the available categories.

    Returns
    -------
    categories_parsed : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
    """
    categories_parsed = {}
    for category in categories:
        id = category["id"]
        label = category["name"]
        categories_parsed[id] = label
    return categories_parsed


def get_and_save_city_events(city, filename="./csv/{}.csv", code_list=None,
                             categories=None, write_date=True, write_name=True,
                             write_id=True):
    """'r'
    It retrieves all the events of a city and arrange them by their categories.
    It can also retrieve information about the date and the description of the
    events. Then, it writes down a custom csv file with this data.

    Parameters
    ----------
    city : string
        Name of the city.
    filename : string
        It tells the directory where to search for the custom csv file. If it
        does not exist, a new file will be created with the directory specified
        in this filename variable.
    code_list : either string or list of strings
        It is a string that contains the country code where the city belongs
        to. In case of cities from United States, a state code is also
        mandatory. Then, code_list is defined as a list of strings made up of
        the country code and the state code.
    categories : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
    write_date : boolean
        When set to true, it will write down the information about the event
        dates to the csv file.
    write_name : boolean
        When set to true, it will write down the name for each event to the csv
        file.
    write_id : boolean
        When set to true, it will write down the id for each event to the csv
        file.
    """
    # Retrieve the required information if not given in the parameters input
    if code_list is None:
        if city in cities:
            code_list = cities[city]
        else:
            print("{} is not in the cities list. A code_list for this city" +
                  "must be specified in the function parameters")
            sys.exit(0)

    if categories is None:
        categories = local_categories

    # Start data request
    print("Searching for all the events in {}".format(city))
    os.makedirs(os.path.dirname(filename.format(city)), exist_ok=True)
    with open(filename.format(city), 'w') as f:
        num_activities = 0
        for category_id, category_label in categories.items():
            results = get_open_events_of_city(city, code_list,
                                              category_id=category_id)
            parsed_data = data_parser(results, write_date, write_name,
                                      write_id)
            num_activities += len(parsed_data)
            write_data(city, parsed_data, category_id, f)
        write_num_activities(city, num_activities, f)

    print("Saved a custom csv file saved in" +
          "\'{}\'".format(filename.format(city)))
