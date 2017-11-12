import json
import csv
import gmaps
# import colorschemes
from matplotlib.cm import Greys, plasma, inferno, viridis
from matplotlib.colors import to_hex


def load_districts_layer(city, colorscheme, opacity=None, invert=False):
    """
    Loads and computes for a given city a layer corresponding to the district's population density

    Parameters
    ----------
    city : string
        Name of the city to which the csv belongs

    Returns
    -------
    gmaps geojson layer for mapping

    """
    with open('geojson/{}.geojson'.format(city), 'r') as f:
        districts_geometry = json.load(f)
    colors = []
    districts = read_district_density_csv(city)
    district_colors = calculate_color(districts, colorscheme, invert=invert)
    for elem in districts_geometry['features']:
        current_name = elem['properties'].get('name') or elem['properties'].get('spatial_alias')
        colors.append(district_colors[current_name])

    # set opacity if no argument given
    if opacity is None:
        opacity = 1
    return gmaps.geojson_layer(districts_geometry, fill_color=colors, stroke_color=colors, fill_opacity=opacity)


def read_district_density_csv(city):
    """
    Reads a district density csv file of the format:

    Mitte;1245
    Friedrichshain-Kreuzberg;5124
    ...
    ...
    Pankow;1424

    Parameters
    ----------
    city : string
        Name of the city to which the csv belongs
    Returns
    -------
    districts : dictionary with districts as a key and its population density as a value
    """
    districts = {}
    with open('districts/{}.csv'.format(city), 'r') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            districts[row[0]] = float(row[1])
    return districts


def calculate_color(density_dict, colorscheme=None, invert=False):
    """
    Transforms the population densities to a gmap color for mapping
    Parameters
    ----------
    density_dict : dict
        dictionary with districts as a key and its population density as a value
    Returns
    -------
    gmaps_color : dict
        dictionary with districts as a key and its gmap color
    """
    # get the biggest population density in the set
    biggest_density = max([x for _, x in density_dict.items()])

    # normalize the density according to the maximum
    normalized_values = {key: val / biggest_density for key, val in density_dict.items()}

    if invert:
        # invert values v-> (1-v)
        normalized_values = {key: 1 - val for key, val in normalized_values.items()}

    # define matplotlib colorscheme
    if colorscheme == 'Greys':
        colorscheme_func = Greys
    elif colorscheme == 'plasma':
        colorscheme_func = plasma
    elif colorscheme == 'inferno':
        colorscheme_func = inferno
    else:
        colorscheme_func = Greys

    # transform the normalized density to a matplotlib color
    mpl_color = {key: colorscheme_func(val) for key, val in normalized_values.items()}

    # transform from a matplotlib color to a valid CSS color
    gmaps_color = {key: to_hex(val, keep_alpha=False) for key, val in mpl_color.items()}
    return gmaps_color
