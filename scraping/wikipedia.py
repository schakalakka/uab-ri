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
    url = (co.WIKIPEDIA_URL.format(language) + search_key).replace(" ", "_")
    response = requests.get(url, headers=co.HEADERS)
    return response


def parse_http_response(response, parser="lxml"):
    soup = BeautifulSoup(response.content, parser)
    return soup


def get_wikipedia_infobox(soup):
    infobox = soup.find('table', class_='infobox')
    return infobox


def get_wikipedia_tables(soup):
    list_of_tables = soup.findAll('table', class_='wikitable')

    if soup.find('table',
                 class_='wikitable sortable jquery-tablesorter') is not None:
        for table in soup.find('table',
                               class_='wikitable sortable jquery-tablesorter'):
            list_of_tables.append(table)

    return list_of_tables


def get_population_data(infobox, keywords=("Total",)):
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


def parse_population_data(data):
    data = data.split("[")[0]
    return data


def scrap_city_population(city, language="en",
                          keywords_to_scrap=(("Density",), ("Total", "City"))):
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
    html_fragment = str(html_fragment)
    if "colspan=\"" in html_fragment:
        html_fragment = html_fragment.split("colspan=\"")[1]
        html_fragment = html_fragment.split("\"")[0]
        return int(html_fragment)
    else:
        return 1


def string_parser(string):
    string = str(string)
    if '\n' in string:
        string = string.replace('\n', '')
    string = string.replace('*', '')
    return string


def float_parser(string, language):
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
    for district_name, data in district_data.items():
        # Conversion from hectare to km2
        if data['Area'] is not None:
            data['Area'] = data['Area'] * 0.01
        if data['Density'] is not None:
            data['Density'] = data['Density'] * 100
    return district_data


def scrap_districts_population(city, source_of_paths=co.SEARCH_PATHS,
                               source_of_languages=co.LANGUAGES):
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
    os.makedirs(os.path.dirname(filename.format(city)), exist_ok=True)

    with open(filename.format(city), 'w') as f:
        writer = csv.writer(f, delimiter=';')

        for data in district_data:
            for key, value in data.items():
                writer.writerow((key, value["Population"], value["Density"],
                                value["Area"]))

    print("The following csv file was written: " +
          "\'{}\'".format(filename.format(city)))
