# To read district densities csv files
import csv

# To handle colors
from matplotlib.cm import plasma, inferno, Greys, viridis
from matplotlib.colors import to_hex


def read_district_density_csv(city):
    """
    Reads a district density csv file of the format:
    District;Population;Population density;area in sqm
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
    districts : dict
        Dictionary with districts as a key and its population density
        as a value
    """
    districts = {}

    with open('districts/{}.csv'.format(city), 'r') as f:
        reader = csv.reader(f, delimiter=';')

        for row in reader:
            districts[row[0]] = float(row[2])

    return districts


def calculate_color(density_dict, colorscheme=None, invert=False):
    """
    Transforms the population densities to a gmap color for mapping

    Parameters
    ----------
    density_dict : dict
        Dictionary with districts as a key and its population density as a
        value

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
