WIKIPEDIA_URL = "http://{}.wikipedia.org/wiki/"

HEADERS = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)' +
           'AppleWebKit/537.11 (KHTML, like Gecko)'}

LANGUAGES = ["en", "es", "de"]

SEARCH_PATHS_EN = ["Districts of {}", "Boroughs and neighborhoods of {}",
                   "Boroughs and quarters of {}", "Boroughs of {}",
                   "List_of_{}_boroughs",
                   "List_of_municipalities_of_the_{}-Capital_Region",
                   "Regional districts of {}"]

SEARCH_PATHS_ES = ["Distritos de {}", "Barrios de {}"]

SEARCH_PATHS_DE = ["Stadtbezirke {}", ]

SEARCH_PATHS = {LANGUAGES[0]: SEARCH_PATHS_EN,
                LANGUAGES[1]: SEARCH_PATHS_ES,
                LANGUAGES[2]: SEARCH_PATHS_DE}

NAME_LIST = {LANGUAGES[0]: ("District", "Borough", "Name", "French name"),
             LANGUAGES[1]: ("Nombre", ),
             LANGUAGES[2]: ("Stadtbezirk", )}

POPULATION_LIST = {LANGUAGES[0]: ("Population", "Residents"),
                   LANGUAGES[1]: ("Población", ),
                   LANGUAGES[2]: ("Einwohner", )}

DENSITY_LIST = {LANGUAGES[0]: ("Density", "Population density"),
                LANGUAGES[1]: ("Densidad", ),
                LANGUAGES[2]: ("Dichte", )}

AREA_LIST = {LANGUAGES[0]: ("Area", "Size"),
             LANGUAGES[1]: ("Area", ),
             LANGUAGES[2]: ("Fläche", )}
