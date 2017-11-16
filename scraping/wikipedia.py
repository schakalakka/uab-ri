# Import requests package to make url requests to Wikipedia
import requests
from requests.exceptions import HTTPError

# Import sys package to finish the script when required
import sys

# Import os to create file directories
import os

# Import csv package to write csv files
import csv

# Import re to parse strings
import re

# To copy variables
import copy

# Import BeautifulSoup to parse html
from bs4 import BeautifulSoup

# Import local constants file
from . import constants as co


def get_wikipedia_response(search_key, language="en"):
    """
    It attempts to get a response from a Wikipedia url.

    Parameters
    ----------
    search_key : string
        This is the Wikipedia url direction.
    language : strin
        It is the language abbreviation that decides in which language a
        Wikipedia page must be search for.

    Returns
    -------
    response : response object
        It is the html response of the web address searched.
    """
    url = (co.WIKIPEDIA_URL.format(language) + search_key).replace(" ", "_")
    response = requests.get(url, headers=co.HEADERS)
    return response


def parse_http_response(response, parser="lxml"):
    """
    This function parses the html response by using BeautifulSoup.

    Parameters
    ----------
    response : response object
        It is an html response of a website.
    parser : string
        It stablishes which BeautifulSoup parser is going to be used.

    Returns
    -------
    soup : BeautifulSoup object
        It contains the html-parsed data.
    """
    soup = BeautifulSoup(response.content, parser)
    return soup


# Deprecated
def get_wikipedia_infobox(soup):
    """
    This function looks for a Wikipedia infobox.

    Parameters
    ----------
    soup : BeautifulSoup object
        It contains the html-parsed data.

    Returns
    -------
    infobox : BeautifulSoup object
        It contains the parsed infobox found, if any.
    """
    infobox = soup.find('table', class_='infobox')
    return infobox


def get_wikipedia_tables(soup):
    """
    This function looks for all Wikipedia tables.

    Parameters
    ----------
    soup : BeautifulSoup object
        It contains the html-parsed data.

    Returns
    -------
    list_of_tables : list of BeautifulSoup objects
        It is a list containing all the tables found in the page, if any.
    """

    list_of_tables = soup.findAll('table', class_='wikitable')

    if soup.find('table',
                 class_='wikitable sortable jquery-tablesorter') is not None:
        for table in soup.find('table',
                               class_='wikitable sortable jquery-tablesorter'):
            list_of_tables.append(table)

    return list_of_tables


# Deprecated
def get_population_data(infobox, keywords=("Total",)):
    """
    It gets the population data from a Wikipedia infobox.

    Parameters
    ----------
    infobox : BeautifulSoup object
        It contains the parsed Wikipedia infobox.
    keywords : list of strings
        Theses are all the keyword to search for in the Wikipedia infobox.

    Returns
    -------
    scraped_data : string
        It is a string with the information that was found in the Wikipedia
        infobox.
    """
    trs = infobox.findAll('tr')

    for tr in trs:
        if tr.has_attr('class'):
            if tr['class'][0] == "mergedtoprow":
                for th in tr.findAll('th'):
                    if th.text.split(" ")[0] == "Population":
                        row = tr.findNextSibling()

    while(row['class'][0] == "mergedrow"):
        cell = row.findChild()

        for keyword in keywords:
            if keyword in cell.text:
                return cell.findNextSibling().text

        row = row.findNextSibling()

    sys.exit("Keywords {} were not found in the ".format(str(keywords)) +
             "population section of Wikipedia's infobox.")


# Deprecated
def parse_population_data(data):
    """
    It parses population data.

    Parameters
    ----------
    data : string
        String containing the scraped data from a Wikipedia infobox.

    Returns
    -------
    data : string
        Parsed string.
    """
    data = data.split("[")[0]
    return data


# Deprecated
def scrap_city_population(city, language="en",
                          keywords_to_scrap=(("Density",), ("Total", "City"))):
    """
    It scraps the population number for a given city from the infobox of its
    Wikipedia page.

    Parameters
    ----------
    city : string
        Name of the city.
    language : strin
        It is the language abbreviation that decides in which language a
        Wikipedia page must be search for.
    keywords_to_scrap : list of lists of strings
        These are all the keywords that will be searched for in the Wikipedia
        infobox.
    """
    response = get_wikipedia_response(city, language)

    try:
        response.raise_for_status()

    except HTTPError:
        sys.exit("Unable to find a page about {} in ".format(city) +
                 "Wikipedia website")

    parsed_response = parse_http_response(response)
    infobox = get_wikipedia_infobox(parsed_response)

    parsed_scraped_data = []

    for keywords in keywords_to_scrap:
        scraped_data = get_population_data(infobox, keywords)

        if scraped_data is None:
            sys.exit("Keywords {} were not found ".format(str(keywords)) +
                     "in the population section of Wikipedia's infobox.")

        parsed_scraped_data.append(parse_population_data(scraped_data))

    return parsed_scraped_data


def get_population_tables(city, language, search_path):
    """
    It looks if a Wikipedia page has suitable tables that may contain
    information about the disctricts population of a city.

    Parameters
    ----------
    city : string
        Name of the city.
    language : string
        It is the language abbreviation that decides in which language a
        Wikipedia page must be search for.
    search_key : string
        This is the Wikipedia url direction.

    Returns
    -------
    list_of_tables : list of BeautifulSoup objects
        This list contains all the tables that were found in this Wikipedia
        page.
    """
    response = get_wikipedia_response(search_path.format(city),
                                      language=language)
    try:
        response.raise_for_status()
        print("Found url \'{}\' ".format(search_path.format(city)) +
              "with information about {} districts.".format(city))
    except HTTPError:
        return None

    parsed_response = parse_http_response(response)
    list_of_tables = get_wikipedia_tables(parsed_response)

    return list_of_tables


def search_colspan(html_fragment):
    """
    It looks for multiple cells and computes how many columns it is made of.

    Parameters
    ----------
    html_fragment : BeautifulSoup object
        It is a html fragment corresponding to a cell of a table.

    Returns
    -------
    width : integer
        It is the width of this cell expressed as the number of columns it
        contains.
    """
    html_fragment = str(html_fragment)
    if "colspan=\"" in html_fragment:
        html_fragment = html_fragment.split("colspan=\"")[1]
        html_fragment = html_fragment.split("\"")[0]
        return int(html_fragment)
    else:
        return 1


def string_parser(string):
    """
    It parses the content of a cell that was identified as a string.

    Parameters
    ----------
    string : BeautifulSoup object
        It is a html fragment corresponding to the content of a cell.

    Returns
    -------
    string : string
        It is the corresponding parsed string.
    """
    string = str(string)
    if '\n' in string:
        string = string.replace('\n', '')
    string = string.replace('*', '')
    return string


def float_parser(string, language):
    """
    It parses the content of a cell that was identified as a float.

    Parameters
    ----------
    string : BeautifulSoup object
        It is a html fragment corresponding to the content of a cell.
    language : string
        It is the language abbreviation that decides in which language this
        cell was written.

    Returns
    -------
    string : float
        It is the corresponding parsed float.
    """

    if string is None:
        return None

    string = str(string)
    string = re.sub('<[^>]+>', ' ', string)

    if not string.strip():
        return None

    if language == "en":
        string = string.replace(',', '')
    else:
        string = string.replace('.', '')
        string = string.replace(',', '.')

    if len(re.findall('\d+\.\d+', string)) == 0:

        if len(re.findall('\d+', string)) > 1:
            if float(re.findall('\d+', string)[0]) > 1000000000:
                string = re.findall('\d+', string)[1]
            else:
                string = re.findall('\d+', string)[0]

    else:
        string = re.findall('\d+\.\d+', string)[0]

    return float(string)


def table_parser(table, language):
    """
    It parses a Wikipedia table with the aim to retrieve population data for
    all the districts of a city.

    Parameters
    ----------
    table : BeautifulSoup object
        It is the html table parsed by BeautifulSoup.
    language : string
        It is the language abbreviation that decides in which language this
        cell was written.

    Returns
    -------
    district_data : dictionary of dictionaries
        It is a dictionary that contains all parsed data that is retrieved from
        the input table. Its format is the following:
            keys:   [district name]
            values: {"Population": float, "Density": float, "Area": float}
    """
    rows = table.findChildren('tr')

    name_col = None
    population_col = None
    density_col = None
    area_col = None

    district_data = {}

    nths = 0

    for nrow, row in enumerate(rows):
        categories = row.findChildren('th')
        nths += 1

        if nrow >= 1 and len(categories) <= 1:
            break

        ncell = 0

        for ncol, category in enumerate(categories):
            current_span = search_colspan(category)
            ncell += current_span

            if category.text.startswith(co.NAME_LIST[language]) and \
                    (name_col is None):
                name_col = ncell - 1
                continue

            elif category.text.startswith(co.POPULATION_LIST[language]) and \
                    (population_col is None):
                population_col = ncell - 1
                continue

            elif category.text.startswith(co.AREA_LIST[language]) and \
                    (area_col is None):
                if (current_span > 1):
                    subcategories = rows[nrow + 1].findChildren('th')
                    if len(subcategories) >= ncell:
                        subcategories = subcategories[
                            (ncell - current_span):ncell]
                        for nsubcell, subcategory in enumerate(subcategories):
                            subcategory = str(subcategory)
                            if "km" in subcategory:
                                area_col = ncell - current_span + nsubcell
                                break
                        continue
                else:
                    area_col = ncell - 1
                    continue

            elif category.text.startswith(co.DENSITY_LIST[language]) and \
                    (density_col is None):
                if (current_span > 1):
                    subcategories = rows[nrow + 1].findChildren('th')
                    if len(subcategories) >= ncell:
                        subcategories = subcategories[
                            (ncell - current_span):ncell]
                        for nsubcell, subcategory in enumerate(subcategories):
                            subcategory = str(subcategory)
                            if "km" in subcategory:
                                density_col = ncell - current_span + nsubcell
                                break
                        continue
                else:
                    density_col = ncell - 1
                    continue

        # print("categories: ", categories)
        # print("cols: ", name_col, population_col, density_col, area_col)

    distr_name = None
    distr_population = None
    distr_density = None
    distr_area = None

    for row in rows[(nths - 1):]:
        if str(row.findChildren()[0]).startswith("<th>"):
            ncell = 1
        else:
            ncell = 0

        cols = row.findChildren('td')
        for col in cols:
            ncell += search_colspan(col)
            if search_colspan(col) > 2:
                continue
            elif name_col is not None and ncell == (name_col + 1):
                distr_name = string_parser(col.text)
            elif population_col is not None and ncell == (population_col + 1):
                distr_population = float_parser(col, language)
            elif density_col is not None and ncell == (density_col + 1):
                distr_density = float_parser(col, language)
            elif area_col is not None and ncell == (area_col + 1):
                distr_area = float_parser(col, language)

        district_data[distr_name] = {"Population": distr_population,
                                     "Density": distr_density,
                                     "Area": distr_area}

    return district_data


def conversion(district_data):
    """
    It converts area and density values that were expressed in hectares into
    kilometers.

    Parameters
    ----------
    district_data : dictionary of dictionaries
        It is a dictionary that contains all parsed data that is retrieved from
        the input table. Its format is the following:
            keys:   [district name]
            values: {"Population": float, "Density": float, "Area": float}

    Returns
    -------
    district_data : dictionary of dictionaries
        It is the same dictionary as the input but it contains the converted
        area and density values expressed in kilometers.
    """
    for district_name, data in district_data.items():
        # Conversion from hectare to km2
        if data['Area'] is not None:
            data['Area'] = data['Area'] * 0.01
        if data['Density'] is not None:
            data['Density'] = data['Density'] * 100
    return district_data


def scrap_districts_population(city, source_of_paths=co.SEARCH_PATHS,
                               source_of_languages=co.LANGUAGES):
    """
    It is the main function to scrap the population data from Wikipedia for all
    the districts of a city.

    Parameters
    ----------
    city : string
        Name of the city.
    source_of_paths : dictionary of keyword lists
        This dictionary has language abbreviations as keys and their
        corresponding keyword lists. It has the following format:
            keys:   [language abbreviation]
            values: [list of "keywords"]
    source_of_languages : list of language abbreviations
        It is a list containing the language abbreviations for all the
        languages whose Wikipedia pages we want to search into.

    Returns
    -------
    data_list : list of dictionaries of dictionaries
        It is a list containing all the population data for all the districts
        of a city. The format of the inner dictionaries is the following:
            keys:   [district name]
            values: {"Population": float, "Density": float, "Area": float}
    """
    list_of_tables = None
    search_paths = copy.deepcopy(source_of_paths)
    languages = copy.deepcopy(source_of_languages)
    language = languages[0]

    while ((list_of_tables is None) and (len(languages) != 0 or
           len(search_paths[language]) != 0)):
        while (len(search_paths[language]) == 0) and (len(languages) != 0):
            language = languages.pop(0)

        if len(search_paths[language]) != 0:
            search_path = search_paths[language].pop(0)
            list_of_tables = get_population_tables(city, language, search_path)

    data_list = []

    if list_of_tables is not None:
        for table in list_of_tables:
            district_data = table_parser(table, language)
            if list(district_data.keys())[0] is not None:
                data_list.append(district_data)

    if len(data_list) == 0:
        print(" No useful information found here, looking somewhere else...")

        if (len(languages) > 0) or (len(search_paths[language]) > 0):
            data_list = scrap_districts_population(city,
                                                   search_paths,
                                                   languages)
        else:
            sys.exit("Unable to find districts of {}".format(city) +
                     " in Wikipedia database")

    if language == "es":
        for data in data_list:
            data = conversion(data)

    return data_list


def write_csv(city, district_data, filename="./districts/{}.csv"):
    """
    This function write the scraped population data to a file.

    Parameters
    ----------
    city : string
        Name of the city.
    data_list : list of dictionaries of dictionaries
        It is a list containing all the population data for all the districts
        of a city. The format of the inner dictionaries is the following:
            keys:   [district name]
            values: {"Population": float, "Density": float, "Area": float}
    filename : string
        Directory and filename of the file that is going to be written.
    """
    os.makedirs(os.path.dirname(filename.format(city)), exist_ok=True)

    with open(filename.format(city), 'w') as f:
        writer = csv.writer(f, delimiter=';')

        for data in district_data:
            for key, value in data.items():
                writer.writerow((key, value["Population"], value["Density"],
                                value["Area"]))

    print("The following csv file was written: " +
          "\'{}\'".format(filename.format(city)))
