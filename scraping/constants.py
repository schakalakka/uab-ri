WIKIPEDIA_URL = "http://{}.wikipedia.org/wiki/"

HEADERS = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)' +
           'AppleWebKit/537.11 (KHTML, like Gecko)'}

LANGUAGES = ["en", "es"]

SEARCH_PATHS_EN = ["Districts of {}", "Boroughs and neighborhoods of {}",
                   "Boroughs and quarters of {}", "Boroughs of {}",
                   "List_of_{}_boroughs"]

SEARCH_PATHS_ES = ["Distritos de {}", "Barrios de {}"]

SEARCH_PATHS = {LANGUAGES[0]: SEARCH_PATHS_EN, LANGUAGES[1]: SEARCH_PATHS_ES}

NAME_LIST = {LANGUAGES[0]: ("District", "Borough", "Name"),
             LANGUAGES[1]: ("Nombre")}

POPULATION_LIST = {LANGUAGES[0]: ("Population", "Residents"),
                   LANGUAGES[1]: ("Población",)}

DENSITY_LIST = {LANGUAGES[0]: ("Density",), LANGUAGES[1]: ("Densidad",)}

AREA_LIST = {LANGUAGES[0]: ("Area", "Size"), LANGUAGES[1]: ("Area",)}
