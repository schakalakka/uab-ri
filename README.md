# uab-ri


The aim of this project is to find and visualize the events posted on Meetup.com in different cities in order to analyze
the density of planned activities and to make a social study regarding typical meeting times and most usual activities
and interests. One aspect may concern different meeting times in Spain and Germany or group size. We will focus our
research on cultural activities like languages tandems and sports. The data shall be obtained via the Meetup-API and
OpenStreetMap. The most important data source for this project is the Meetup-API where we have to request the events
with different Python packages like “requests” or “meetup-api”. Our second task is to visualize the locations of the
events on a given city map obtained by data resources like OpenStreetMap. To plot the locations we could use
“matplotlib” or similar Python plotting libraries.
One further aspect could be to look for interest of twitter users to make recommends to activities nearby. The geotag
of the tweets provides the central information for the search.