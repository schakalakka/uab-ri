# Import custom constants
from . import constants as co

# Import GMaps Package
import gmaps

# Import default libraries
import sys

# Import mu_requests functions
"""
Be aware that here we are importing a module that is in a top level. First we
need to add './..' directory to the system path. This is done in the
__init__.py file.
"""
from meetup.mu_requests import add_key, params, get_categories, categories_parser
from my_keys import MU_KEY


def line_parser(line):
    """
    It parses the input line into a dictionary that contains all the
    information about each event.

    Parameters
    ----------
    line : string
        It contains the information of an event read from a custom csv file.

    Returns
    -------
    parsed_line : dictionary
        Dictionary that contains the parsed data with the following format:
            keys:   ["coordinates", "date", "name", "event_id"]
            values: [2-dim tuple of floats, integer, string, string]
    """
    parsed_line = {}
    splitted_line = line.split(";")
    keys = ["latitude", "longitude", "date", "name", "event_id"]
    if len(splitted_line) != len(keys):
        print("Error while parsing line:\n {}".format(line))
        sys.exit(0)
    for i, value in enumerate(splitted_line):
        parsed_line[keys[i]] = value
    return parsed_line


def read_custom_csv(filename, category_list):
    """
    This function reads a custom csv file containing a list of information
    about all the activities that were found in a city. These coordinates are
    arranged by the category they belong to. Each category has a specific
    category id which is an integer that, currently, goes from 1 to 36 (this
    could change as it depends on whether they add more categories or not).
    The format of this input file is the following:
        #1          indicates the category id where the activities' from below
                    belong to.
        0.0;0.0;... the corresponding information about an event goes here
        ...         information about the other events
        0.0;0.0;... information about another event
        !#          end of the events that belong to the category 1.
    Additionally, the total number of activities that were found in that city
    can be obtained as indicated below:
        #0          this zero does not belong to any category id. It tells us
                    that the information that comes after it is the total
                    number of activities of that city.
        00000       total number of activities
        !#          end of the section

    Parameters
    ----------
    filename : string
        It tells the directory where to search for the custom csv file.
    category_list : list of integers
        These describe all the category ids whose activities we want to search
        for in the file.

    Returns
    -------
    parsed_events : list of dictionaries
        Parent list contains different events. Dictionaries contain the parsed
        data with the following format:
            keys:   ["coordinates", "date", "name", "event_id"]
            values: [2-dim tuple of floats, integer, string, string]
     num_activities : integer
        Total number of activities that have been found in a specific city.

    """
    parsed_events = []
    num_activities = None

    with open(filename, 'r') as f:
        for line in f:
            if(line.startswith("#")):
                category_id = int(line.strip("#").strip())
                if(category_id == 0):
                    line = next(f)
                    num_activities = int(line)
                    line = next(f)
                if(category_id in category_list):
                    line = next(f)
                    while (not line.startswith("!#")):
                        parsed_event = line_parser(line)
                        parsed_events.append(parsed_event)
                        line = next(f)

    return parsed_events, num_activities


def cyclic_iteration(current_position, top):
    """
    Simple function to create a cyclic iteration between 0 and a maximum value
    (top) which is included in the sequence.

    Parameters
    ----------
    current position : integer
        Current position of the iteration.
    top : integer
        Inner limit value for our iteration.

    Returns
    -------
    new_position : integer
        This is the new position of our iteration.
    """
    if current_position < top:
        return current_position + 1
    else:
        return 0


def map_activities(city, categories=None, color_pattern=None,
                   max_intensity=None):
    """
    It creates a gmaps object which is going to be used to plot all the
    activity locations on a map.

    Parameters
    ----------
    city : string
        Name of the city whose activities we want to map.
    categories : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
    color_pattern : string
        A string that defines which color pattern will be used in the plot.
        More information about these patterns in the constants.py file.
    max_intensity : float
        A value that sets the maximum intensity for the heat map.

    Returns
    -------
    my_map : gmaps object
        This object will be used to plot the map and all activities locations
        in a Jupyter Notebook.
    """
    my_map = gmaps.figure()

    if categories is None:
        if 'key' not in params:
            add_key(MU_KEY)
        categories = categories_parser(get_categories())
        print(categories)

    if max_intensity < 0:
        print("Parameter error: max_intensity must be a positive float.")
        sys.out(0)

    # Apply a different color pattern for every layer by using a counter
    counter = 0
    for category_id, category_label in categories.items():
        events_data, num_activities = read_custom_csv(
            './csv/{}.csv'.format(city), [category_id, ])

        locations = []

        # Filter those events with wrong or unknown locations
        for event in events_data:
            latitude = event["latitude"]
            longitude = event["longitude"]
            if ((latitude == "None") or (longitude == "None") or
               (latitude == 0 and longitude == 0)):
                continue
            else:
                locations.append((float(event["latitude"]),
                                 float(event["longitude"])))

        if(len(locations) == 0):
            print("No local activities were found in " +
                  "{} matching category: {}".format(city, category_label))
            continue

        layer = gmaps.heatmap_layer(locations)

        if color_pattern is None:
            for index, item in enumerate(co.COLOR_GRADIENTS.values()):
                if index == counter:
                    layer.gradient = item
                    break
        else:
            try:
                layer.gradient = co.COLOR_GRADIENTS[color_pattern]
            except KeyError:
                print("Wrong color pattern parameter. More information in " +
                      "the constants.py file")

        layer.max_intensity = max_intensity
        layer.point_radius = co.POINT_RADIUS
        my_map.add_layer(layer)

        counter = cyclic_iteration(counter, len(co.COLOR_GRADIENTS) - 2)

    return my_map


def get_categories_subset(categories=None, labels=()):
    """
    It returns a subset of the categories dictionary depending on the category
    labels submitted.

    Parameters
    ----------
    categories : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
    labels : either a string or a list of strings
        It contains the label or a list of the labels whose ids we want to get.

    Returns
    -------
    categories_subset : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
        It is a subset of the submitted categories dictionary.
    """
    categories_subset = {}

    if categories is None:
        if 'key' not in params:
            add_key(MU_KEY)
        categories = categories_parser(get_categories())

    if (type(labels) is not list) and (type(labels) is not tuple):
        labels = [labels, ]

    for label in labels:
        for category_id, category_label in categories.items():
            if category_label == label:
                categories_subset[category_id] = category_label

    return categories_subset
