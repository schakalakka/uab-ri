from mapping import mapping
from meetup import categories, cities
from population_density import population_density_of_whole_city
import pygal

category_list = categories.categories
category_ids = [id for id, name in category_list.items()]
category_names = [name for id, name in category_list.items()]
city_list = cities.cities
population_density_dict = population_density_of_whole_city

activities_per_category = {}
for city in city_list:
    activities_per_category[city] = {}
    for category_id, category_name in category_list.items():
        activities_per_category[city][category_name] = max(0.000000000000000000000000000000000000000001, len(
            mapping.read_custom_csv('../csv/{}.csv'.format(city), {category_id: category_name})[0]))
        activities_per_category[city]['all'] = \
        mapping.read_custom_csv('../csv/{}.csv'.format(city), {category_id: category_name})[1] or 0

print(activities_per_category)


def plot(data, city, categories=None):
    barchart = pygal.HorizontalBar()
    for category in categories:
        if data[city][category] > 0:
            barchart.add(category, data[city][category])
    barchart.render_in_browser()
    barchart.render_to_png('plot.png')


def plot_all_cities(data, citylist=None, category=None, per_capita=False):
    barchart = pygal.HorizontalBar(print_values=False, print_labels=True, print_zeros=True)
    if category is None:
        category = 'all'
    if citylist is None:
        citylist = city_list
    barchart.title = f'Number of Open Events per Million Capita in City; Category: {category}' if per_capita else f'Number of Open Events per City; Category: {category}'
    inhabitants = 1
    for city in citylist:
        if per_capita:
            inhabitants = population_density_dict[city]
        if data[city][category]:
            barchart.add(city, data[city][category]*1000000 / float(inhabitants))
    # barchart.render_in_browser()

    infix = '_per_capita' if per_capita else ''

    barchart.render_to_png(f'pngs/activities_per_city{infix}/{category}.png')
    barchart.render_to_file(f'svgs/activities_per_city{infix}/{category}.svg')


# plot(activities_per_category, 'Berlin', category_names)

plot_all_cities(activities_per_category, citylist=city_list, per_capita=False)
plot_all_cities(activities_per_category, citylist=city_list, per_capita=True)

for category_name in category_names:
    plot_all_cities(activities_per_category, category=category_name, citylist=city_list, per_capita=False)
    plot_all_cities(activities_per_category, category=category_name, citylist=city_list, per_capita=True)
