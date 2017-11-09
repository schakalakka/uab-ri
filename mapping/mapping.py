# Import custom constants
from . import constants as co

# Import GMaps Package
import gmaps

# Import default libraries
import sys

# Import mu_requests functions and MeetUp Key from local files
"""
Be aware that here we are importing a module that is in a top level. First we
need to add './..' directory to the system path. This is done in the
__init__.py file.
"""
from meetup.categories import categories as local_categories


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


def color_patterns_parser(color_patterns):
    """
    This function parses the color patterns input.

    Parameters
    ----------
    color_patterns : either a string or a list of strings
        A string that defines which color pattern will be used in the plot. If
        a color pattern is defined for each category, they will be colored
        according to this list. More information about these patterns in the
        constants.py file.

    Returns
    -------
    color_patterns_parser : list of lists
        A list of lists. Each child list contains information about one color
        pattern.
    """
    parsed_color_patterns = []
    if color_patterns is None:
        parsed_color_patterns = co.COLOR_GRADIENTS_LIST

    elif color_patterns == "default":
        parsed_color_patterns.append(co.DEFAULT_GRADIENT)

    elif ((type(color_patterns) is not list) and
          (type(color_patterns) is not tuple)):
        try:
            parsed_color_patterns.append(co.COLOR_GRADIENTS[color_patterns])
        except KeyError:
            print("Wrong color pattern parameter. More information " +
                  "in the constants.py file")

    else:
        for color in color_patterns:
            try:
                parsed_color_patterns.append(co.COLOR_GRADIENTS[color])
            except KeyError:
                print("Wrong color pattern \'{}\' parameter. ".format(color) +
                      "More information in the constants.py file")

    return parsed_color_patterns


def map_activities(city, categories=None, color_patterns=None,
                   max_intensity=1):
    """
    It creates a gmaps object which is going to be used to plot all the
    activity locations on a map.

    Parameters
    ----------
    city : string
        Name of the city whose activities we want to map.
    categories : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
    color_patterns : either a string or a list of strings
        A string that defines which color pattern will be used in the plot. If
        a color pattern is defined for each category, they will be colored
        according to this list. More information about these patterns in the
        constants.py file.
    max_intensity : float
        A value that sets the maximum intensity for the heat map.

    Returns
    -------
    my_map : gmaps object
        This object will be used to plot the map and all activities locations
        in a Jupyter Notebook.
    """
    my_map = gmaps.figure()

    # Define initial variables, if needed
    if categories is None:
        categories = local_categories

    if max_intensity < 0:
        print("Parameter error: max_intensity must be a positive float.")
        sys.out(0)

    parsed_color_patterns = color_patterns_parser(color_patterns)

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
               (latitude == "0" and longitude == "0")):
                continue
            else:
                locations.append((float(event["latitude"]),
                                 float(event["longitude"])))

        if(len(locations) == 0):
            print("No local activities were found in " +
                  "{} matching category: {}".format(city, category_label))
            continue

        layer = gmaps.heatmap_layer(locations)

        layer.gradient = parsed_color_patterns[counter]

        layer.max_intensity = max_intensity
        layer.point_radius = co.POINT_RADIUS
        my_map.add_layer(layer)

        counter = cyclic_iteration(counter, len(parsed_color_patterns) - 1)

    return my_map


def get_categories_subset(labels=(), categories=None):
    """
    It returns a subset of the categories dictionary depending on the category
    labels submitted.

    Parameters
    ----------
    labels : either a string or a list of strings
        It contains the label or a list of the labels whose ids we want to get.
    categories : dictionary of categories
        This dictionary has category ids as keys and category labels as items.

    Returns
    -------
    categories_subset : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
        It is a subset of the submitted categories dictionary.
    """
    categories_subset = {}

    if categories is None:
        categories = local_categories

    if (type(labels) is not list) and (type(labels) is not tuple):
        labels = [labels, ]

    not_found = []

    for label in labels:
        for category_id, category_label in categories.items():
            if category_label == label:
                categories_subset[category_id] = category_label
                break
        else:
            not_found.append(label)

    for label in not_found:
        print("Category label \'{}\' was not found in ".format(label) +
              "MeetUp categories list.")

    if len(categories_subset) == 0:
        print("Warning: the categories subset created is empty.")

    return categories_subset
