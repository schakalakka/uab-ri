# Import custom constants
from . import constants as co

# Import custom district functions
from . import districts as distr

# Import GMaps Package
import gmaps

# Import default libraries
import sys
from datetime import datetime
import json

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
            if (line.startswith("#")):
                category_id = int(line.strip("#").strip())
                if (category_id == 0):
                    line = next(f)
                    num_activities = int(line)
                    line = next(f)
                if (category_id in category_list):
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


def get_datetime_object(year=None, month=None, day=None, hour=None,
                        minut=None, second=None):
    """
    This function creates a new datetime object by calling datetime() method.

    Parameters
    ----------
    year : integer
        It specifies the year.
    month : integer
        It specifies the month.
    day : integer
        It specifies the day.
    hour : integer
        It specifies the hour.
    minut : integer
        It specifies the minut.
    second : integer
        It specifies the second.
    """
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    if day is None:
        day = now.day
    if hour is None:
        hour = 0
    if minut is None:
        minut = 0
    if second is None:
        second = 0

    return datetime(year, month, day, hour, minut, second)


def datetime_parser(datetime_list):
    """
    It parses a list of datetime objects. The output is a list of 2-dimensional
    tuples. Each tuple defines a time interval.

    Parameters
    ----------
    datetime_list : list of arranged timetable objects
        It contains the list of timetable objects given as input. If they come
        separated by single commas they will be treated separately. In this
        case, the time interval will be defined by using the current date as
        the other limit for the time interval. If hours are given in pairs of
        two by using 2-dimensional tuples or lists, each pair will be used to
        describe a time interval itself.

    Returns
    -------
    parsed_datetime : list of 2-dimensional tuples
        Tuples contain the limits for the time intervals expressed by datetime
        objects.
    """
    now = datetime.now().replace(microsecond=0)
    parsed_datetime = []

    for datetime_object in datetime_list:

        if ((type(datetime_object) is not list) and
                (type(datetime_object) is not tuple)):

            if datetime_object < now:
                parsed_datetime.append((datetime_object, now))

            else:
                parsed_datetime.append((now, datetime_object))
        else:
            if datetime_object[0] > datetime_object[1]:
                parsed_datetime.append((datetime_object[1],
                                        datetime_object[0]))

            else:
                parsed_datetime.append((datetime_object[0],
                                        datetime_object[1]))

    return parsed_datetime


def locations_parser(data, time_interval=None):
    """
    It retrieves the right locations from events data, according to the filters
    supplied, and parses them.

    Parameters
    ----------
    data : list of dictionaries
        Parent list contains different events. Dictionaries contain the parsed
        data with the following format:
            keys:   ["coordinates", "date", "name", "event_id"]
            values: [2-dim tuple of floats, integer, string, string]
    time_interval : 2-dimensional tuple
        Contain the limits of the time interval where we want to search for
        events.

    Returns
    -------
    parsed_locations : list of 2-dimensional tuples
        Each tuple contain the latitude and the longitude of the location for
        each event.
    """
    parsed_locations = []

    for event in data:
        event_date = datetime.fromtimestamp(int(event.get("date")) / 1000)
        if time_interval is not None:
            if ((time_interval[0] > event_date) or
                    (event_date > time_interval[1])):
                continue

        latitude = event.get("latitude")
        longitude = event.get("longitude")

        if ((latitude == "None") or (longitude == "None") or
                (latitude == "0" and longitude == "0")):
            continue

        else:
            parsed_locations.append((float(event["latitude"]),
                                     float(event["longitude"])))

    return parsed_locations


def map_activities(city, categories=None, time_intervals=None,
                   color_patterns=None, max_intensity=1, geojson=False,
                   geojson_options={}):
    """
    It creates a gmaps object which is going to be used to plot all the
    activity locations on a map.

    Parameters
    ----------
    city : string
        Name of the city whose activities we want to map.
    categories : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
    time_intervals : either a datetime object or a list of datetime objects
        Each datetime object describes either both limits of a time interval or
        just one. In this last case, the time interval is calculated by using
        the current time as the other limit of the timer interval.
    color_patterns : either a string or a list of strings
        A string that defines which color pattern will be used in the plot. If
        a color pattern is defined for each category, they will be colored
        according to this list. More information about these patterns in the
        constants.py file.
    max_intensity : float
        A value that sets the maximum intensity for the heat map.
    geojson : boolean
        If True it uses a geojson file of city to map an additional population
        density layer
    geojson_options : dict
        Dictionary containing geojson options like
            colorscheme = 'Greys','viridis','inferno','plasma'
            invert = True or False for inverting the colorscheme
            opacity = int in the range of [0,1]

    Returns
    -------
    my_map : gmaps object
        This object will be used to plot the map and all activities locations
        in a Jupyter Notebook.
    """
    my_map = gmaps.figure()

    # If geojson==True use an additional layer for the population density
    if geojson:
        colorscheme = geojson_options.get('colorscheme')
        opacity = geojson_options.get('opacity')
        invert = geojson_options.get('invert', False)
        districts_layer = load_districts_layer(
            city, colorscheme=colorscheme, opacity=opacity, invert=invert)

        my_map.add_layer(districts_layer)

    # Define initial variables, if needed
    if categories is None:
        categories = local_categories

    if max_intensity < 0:
        print("Parameter error: max_intensity must be a positive float.")
        sys.out(0)

    parsed_color_patterns = color_patterns_parser(color_patterns)

    # Apply a different color pattern for every layer by using a counter
    counter = 0

    # Choose an iterator depending on the filter chosen in the input parameters
    iterator = categories.items()
    iterator_type = "category"

    if time_intervals is not None:
        time_intervals = datetime_parser(time_intervals)
        iterator = enumerate(time_intervals)
        iterator_type = "time interval"

    for index, value in iterator:
        if iterator_type == "category":
            events_data, num_activities = read_custom_csv(
                './csv/{}.csv'.format(city), [index, ])
            # Filter those events with wrong or unknown locations
            locations = locations_parser(events_data)

        elif iterator_type == "time interval":
            events_data, num_activities = read_custom_csv(
                './csv/{}.csv'.format(city), [i for i in categories])
            # Filter those events with wrong or unknown locations
            locations = locations_parser(events_data, value)

        if (len(locations) == 0):
            print("No local activities were found in " +
                  "{} matching {}: {}".format(city, iterator_type, value))
            continue

        layer = gmaps.heatmap_layer(locations)

        layer.gradient = parsed_color_patterns[counter]

        layer.max_intensity = max_intensity
        layer.point_radius = co.POINT_RADIUS
        my_map.add_layer(layer)

        counter = cyclic_iteration(counter, len(parsed_color_patterns) - 1)

    return my_map


def paint_districts(city, categories=None, time_intervals=None,
                    colorscheme='Grays', opacity=None,
                    per_capita=False):
    """
    It creates a gmaps object which is going to be used to paint all the
    districts in a city according to the number of MeetUp activities that they
    contain.

    Parameters
    ----------
    city : string
        Name of the city whose activities we want to map.
    categories : dictionary of categories
        This dictionary has category ids as keys and category labels as items.
    time_intervals : either a datetime object or a list of datetime objects
        Each datetime object describes either both limits of a time interval or
        just one. In this last case, the time interval is calculated by using
        the current time as the other limit of the timer interval.
    max_intensity : string
        It defines the colorscheme that will be used in the painting of the
        districts. It supports: 'Greys','viridis','inferno and 'plasma'.
    opacity : float
        It defines the opacity of the district layers. It supports a value in
        the range of [0,1]
    per_capita : boolean
        If true, and if counter_data is provided, it will paint districts
        according to the (Number of activites in a district) / (Population in
        this district) ratio.

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

    events_data, num_activities = read_custom_csv(
        './csv/{}.csv'.format(city), [i for i in categories])

    counter = distr.events_per_district(events_data,
                                        './geojson/{}.geojson'.format(city))

    districts_layer = load_districts_layer(city, colorscheme=colorscheme,
                                           counter_data=counter,
                                           opacity=opacity,
                                           per_capita=per_capita)
    my_map.add_layer(districts_layer)

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


def load_districts_layer(city, colorscheme, counter_data=None,
                         opacity=None, invert=False, per_capita=False):
    """
    Loads and computes for a given city a layer corresponding to the
    district's population density

    Parameters
    ----------
    city : string
        Name of the city to which the csv belongs
    colorscheme : string
        It defines the colorscheme that will be used in the painting of the
        districts. It supports: 'Greys','viridis','inferno and 'plasma'.
    counter_data : dictionary
        If supplied, it will help to paint the districts according to the
        number of activities that each one has.
    opacity : float
        It defines the opacity of the district layers. It support values
        between 0 and 1.
    invert : boolean
        If true, it inverts the colors of the colorscheme.
    per_capita : boolean
        If true, and if counter_data is provided, it will paint districts
        according to the (Number of activites in a district) / (Population in
        this district) ratio.

    Returns
    -------
    gmaps geojson layer for mapping
    """
    with open('geojson/{}.geojson'.format(city), 'r') as f:
        districts_geometry = json.load(f)
    if counter_data is None:
        colors = []
        districts = distr.read_district_density_csv(city)
        district_colors = distr.calculate_color(districts, colorscheme,
                                                invert=invert)
    else:
        if per_capita:
            population = distr.read_district_population_csv(city)
            density = {}
            for district_name, events_number in counter_data.items():
                if district_name == "Not Located":
                    continue
                density[district_name] = events_number / \
                    population[district_name]
        else:
            density = counter_data

        colors = []
        districts = distr.read_district_density_csv(city)
        district_colors = distr.calculate_color(density, colorscheme,
                                                invert=invert)

    for elem in districts_geometry['features']:
        current_name = elem['properties'].get('name') or elem['properties'].get('spatial_alias') or \
                       elem['properties'].get('stadtbezirk') or elem['properties'].get('neighbourhood')
        colors.append(district_colors[current_name])

    # set opacity if no argument given
    if opacity is None:
        opacity = co.LAYER_TRANSPARENCY

    return gmaps.geojson_layer(districts_geometry, fill_color=colors,
                               stroke_color=colors, fill_opacity=opacity)
