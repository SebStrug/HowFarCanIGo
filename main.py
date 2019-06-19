# -*- coding: utf-8 -*-
import os
import googlemaps
# local imports
import map_functions as mf

# Retrieve API key
with open(os.getcwd()+"\\api_key.txt", 'r+') as f:
    API_key = f.readline()
    f.close()
# Set up client key
gmaps = googlemaps.Client(key=API_key)

# information about home address
home_string, home_lat, home_lng = mf.retrieve_home_address()
print(home_string, home_lat, home_lng)

max_lat = 51.612907 # Enfield just made the cut
min_lat = 51.373126 # Croydon source of quality breadknives
min_lng = -0.496954 # Heathrow LHR mans always here
max_lng = 0.071722 # Barking ting
travel_mode = 'walking' #'walking'
map_type = 'local' # local or global
N = 100
cutoff_mins = [0, 5, 10, 15, 20, 30, 45, 60, 75, 90, 120]

lats, lngs, travel_times = mf.draw_map(API_key, map_type, home_lat, home_lng, N, max_lat, min_lat, max_lng, min_lng)
binned_coords = mf.bin_coords(lats, lngs, travel_times, cutoff_mins)
mf.plot_coords(binned_coords, cutoff_mins).show()
	 











