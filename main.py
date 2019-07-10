# -*- coding: utf-8 -*-
import os
import googlemaps
# local imports
import generate_map as gen_map
import draw_map
import debug as db
import hulls

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

## Add home marker to map, and maybe tube stops, play with having more layers etc.

# Retrieve API key
with open(os.getcwd()+"\\api_key.txt", 'r+') as f:
    API_key = f.readline()
    f.close()
# Set up client key
gmaps = googlemaps.Client(key=API_key)

# information about home address
home_string, home_lat, home_lng = gen_map.retrieve_home_address()
print(home_string, home_lat, home_lng)

max_lat = 51.612907 # Enfield just made the cut
min_lat = 51.373126 # Croydon source of quality breadknives
min_lng = -0.496954 # Heathrow LHR mans always here
max_lng = 0.071722 # Barking ting
travel_mode = 'transit' #'walking'
map_type = 'local' # local or global
N = 100
cutoff_mins = [0, 10, 20, 30, 45, 60, 75, 60*1.5, 60*2, 60*3]

lats, lngs, travel_times = gen_map.generate_points(API_key, map_type, home_lat, home_lng, N, max_lat, min_lat, max_lng, min_lng, travel_mode)
binned_coords = draw_map.bin_coords_by_cutoff(lats, lngs, travel_times, cutoff_mins)
print('Number of values associated with each cut-off time:')
for val in range(1,len(cutoff_mins)):
    print('Cutoff time: ', cutoff_mins[val], ', Number of points: ', len(binned_coords[val]))
cutoff_hull_arrays = draw_map.generate_hull_arrays(binned_coords, 3)


# Draw the map in a matplot graph
fig, ax = plt.subplots()
for cutoff_index, cutoff_points in enumerate(cutoff_hull_arrays):
	for island_index, island_points in enumerate(cutoff_points):
		ax.fill(island_points[:,0], island_points[:,1], color='b', alpha=0.4)
fig.show()

# Draw the map in a folium map
my_map = folium.Map(location=[home_lat, home_lng], zoom_start=10) # Initialize map
for cutoff_index, cutoff_points in enumerate(cutoff_hull_arrays):
	draw_map.add_cutoff_points(my_map, cutoff_points, layer_name='Cutoff {} mins'.format(cutoff_mins[cutoff_index+1]),
								line_color='lightblue', fill_color='royalblue', weight=2, text='foo')
folium.LayerControl(collapsed=False).add_to(my_map) # Add layer control and show map
my_map.save('new_map.html')


def draw_points(map_object, list_of_points, layer_name, line_color, fill_color, text):
	"""FUTURE: IMPROVE, DOCUMENT, MAKE USABLE"""
    fg = folium.FeatureGroup(name=layer_name)
    for point in list_of_points:
        fg.add_child(folium.CircleMarker(point, radius=1, color=line_color, fill_color=fill_color,
                                         popup=(folium.Popup(text))))
    map_object.add_child(fg)



