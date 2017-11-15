# To read district densities csv files
import csv

# To handle colors
from matplotlib.cm import plasma, inferno, Greys, viridis
from matplotlib.colors import to_hex

# To work with json formatted files
import json

# To work with polygons
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Import local libraries
from . import mapping as mp
from . import constants as co


def read_district_csv(city, key="Density"):
    """
    Reads a district data from a csv file with the following format:
        District;Population;Population density per sqm;area in sqm
    For instance:
        Evere;39556.0;7911.0;5.0
        Schaerbeek;132590.0;16369.0;8.1
        ...
        Etterbeek;47180.0;15219.0;3.1

    Parameters
    ----------
    city : string
        Name of the city to which the csv belongs
    key : string
        It tells which data to retrieve from the csv file.

    Returns
    -------
    districts : dict
        Dictionary with districts as a key and its corresponding data as a
        value.
    """
    districts = {}

    with open('districts/{}.csv'.format(city), 'r') as f:
        reader = csv.reader(f, delimiter=';')

        index = co.CSV_FORMAT_TRANSLATOR[key]

        for row in reader:
            try:
                districts[row[0]] = float(row[index])
            except:
                if key=='Density':
                    districts[row[0]] = float(row[1])/float(row[3])
                else:
                    print('Some error occured. Is the districts.csv file correct?')
    return districts


def calculate_color(density_dict, colorscheme=None, counter_data=None,
                    invert=False):
    """
    Transforms the population densities to a gmap color for mapping

    Parameters
    ----------
    density_dict : dict
        Dictionary with districts as a key and its population density as a
        value
    colorscheme : string
        It defines the colorscheme that will be used in the painting of the
        districts. It supports: 'Greys','viridis','inferno and 'plasma'.
    counter_data : dictionary
        If supplied, it will help to paint the districts according to the
        number of activities that each one has.
    invert : boolean
        If true, it inverts the colors of the colorscheme.

    Returns
    -------
    gmaps_color : dict
        Dictionary with districts as a key and its gmap color
    """
    # get the biggest population density in the set
    biggest_density = max([x for _, x in density_dict.items()])

    # normalize the density according to the maximum
    normalized_values = {key: val / biggest_density for key, val in
                         density_dict.items()}

    if invert:
        # invert values v-> (1-v)
        normalized_values = {key: 1 - val for key, val in
                             normalized_values.items()}

    """
        if counter_data is None:
        # get the biggest population density in the set
        biggest_density = max([x for _, x in density_dict.items()])

        # normalize the density according to the maximum
        normalized_values = {key: val / biggest_density for key, val in
                             density_dict.items()}

        if invert:
            # invert values v-> (1-v)
            normalized_values = {key: 1 - val for key, val in
                                 normalized_values.items()}
    else:
        for district_name in counter_data.items():
            # get the biggest number of activities per district in the set
            biggest_density = max([x for _, x in density_dict.items()])

    """

    # define matplotlib colorscheme
    if colorscheme == 'Greys':
        colorscheme_func = Greys
    elif colorscheme == 'plasma':
        colorscheme_func = plasma
    elif colorscheme == 'inferno':
        colorscheme_func = inferno
    elif colorscheme == 'viridis':
        colorscheme_func = viridis
    else:
        colorscheme_func = Greys

    # transform the normalized density to a matplotlib color
    mpl_color = {key: colorscheme_func(val) for key, val in
                 normalized_values.items()}

    # transform from a matplotlib color to a valid CSS color
    gmaps_color = {key: to_hex(val, keep_alpha=False) for key, val in
                   mpl_color.items()}

    return gmaps_color


def events_per_district(events, geojson_filename):
    """
    This function tries to localize all the event of a city on its districts.

    Parameters
    ----------
    events : list of dictionaries
        These are the event we want to localize. Parent list contains different
        events. Dictionaries contain the parsed data with the following format:
            keys:   ["latitude", "longitude", "date", "name", "event_id"]
            values: [string, string, integer, string, string]
    geojson_filename : string
        It is the direction to a file that contains the information about the
        districts where we expect to find the events from above.

    Returns
    -------
    counter : dictionary
        It is a dictionary whose keys are all the districts where we have been
        found events. Their items are the number of matches that have been
        produced for each district.
    """
    event_locations = mp.locations_parser(events)

    event_points = []

    for event_location in event_locations:
        event_points.append(Point(event_location[1], event_location[0]))

    with open(geojson_filename, 'r') as f:
        districts_geometry = json.load(f)

    districts = districts_geometry['features']
    district_polygons = {}

    for district in districts:
        name = district['properties']['name']
        polygons = []
        if district['geometry']['type'] == "Polygon":
            for polygon in district['geometry']['coordinates']:
                polygons.append(Polygon(polygon))
        elif district['geometry']['type'] == "MultiPolygon":
            for polygon in district['geometry']['coordinates']:
                for subpolygon in polygon:
                    polygons.append(Polygon(subpolygon))

        district_polygons[name] = polygons

    counter = {}

    for district_name, polygons_list in district_polygons.items():
        for district_polygon in polygons_list:
            for event_point in event_points:
                if district_polygon.contains(event_point):
                    event_points.remove(event_point)
                    if district_name not in counter:
                        counter[district_name] = 1
                    else:
                        counter[district_name] += 1

    notlocated = len(event_points)

    # If there is any empty district, added it to get a dictionary consistent
    # with the districts of the city
    for district_name in district_polygons.keys():
        if district_name not in counter.keys():
            counter[district_name] = 0

    counter["Not Located"] = notlocated

    return counter
