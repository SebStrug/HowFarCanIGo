# -*- coding: utf-8 -*-
import os
import googlemaps
# local imports
import generate_map as gen_map
import draw_map
import debug as db
import hulls
import folium
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

## Add home marker to map, and maybe tube stops, play with having more layers etc.
## Options to pickle those hull arrays since they take so long to generate
## Options to draw map or just generate points
## Really smash it and draw loads of points

# Retrieve API key
with open(os.getcwd()+"\\api_key.txt", 'r+') as f:
    API_key = f.readline()
    f.close()
# Set up client key
gmaps = googlemaps.Client(key=API_key)

# information about home address
home_string, home_lat, home_lng = gen_map.retrieve_home_address()
print(home_string, home_lat, home_lng)

# initialise parameters
max_lat = 51.612907 # Enfield just made the cut
min_lat = 51.373126 # Croydon source of quality breadknives
min_lng = -0.496954 # Heathrow LHR mans always here
max_lng = 0.071722 # Barking ting
travel_mode = 'transit' #'walking'
map_type = 'local' # local or global
N = 10
cutoff_mins = [0, 10, 20, 30, 45, 60, 75, 60*1.5, 60*2, 60*3]

# generate points with associated travel times
lats, lngs, travel_times = gen_map.generate_points(API_key, map_type, home_lat=home_lat, home_lng=home_lng, 
													N=N, max_lat=max_lat, min_lat=min_lat, max_lng=max_lng,
													min_lng=min_lng, lat_multiplier=0.002, lng_multiplier=0.003,
													travel_mode_=travel_mode)
assert len(lats) == len(travel_times), 'Different number of coordinates ({}), to travel times ({})'.format(len(lats), len(travel_times))
# group points by travel time
binned_coords = draw_map.bin_coords_by_cutoff(lats, lngs, travel_times, cutoff_mins)
gen_map.describe_cutoffs(cutoff_mins, binned_coords)

#cmap = sns.diverging_palette(250, 15, s=75, l=40, as_cmap=True)
#cmap = sns.color_palette("Paired", n_colors=len(cutoff_mins_)+3)
cmap = sns.dark_palette('yellow', n_colors=5)
#cmap = sns.cubehelix_palette(8, dark=.2, light=.8, reverse=True, as_cmap=True)

# order the points into concave hull arrays
cutoff_hull_arrays = draw_map.generate_hull_arrays(binned_coords, num_bins=4)
draw_map.draw_folium_map(home_lat, home_lng, cutoff_hull_arrays, cutoff_mins, cmap)

