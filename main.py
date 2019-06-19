# -*- coding: utf-8 -*-
import os
import googlemaps
import datetime
import numpy as np
import matplotlib.pyplot as plt
# local imports
import map_functions as mf
import hulls

# Retrieve API key
with open(os.getcwd()+"\\api_key.txt", 'r+') as f:
    API_key = f.readline()
    f.close()
# Set up client key
gmaps = googlemaps.Client(key=API_key)

# information about home address
home_string, home_lat, home_lng = mf.retrieve_home_address()
print(home_string, home_lat, home_lng)

max_lat = 51.612907 # Enfield
min_lat = 51.373126 # Croydon
min_lng = -0.496954 # Heathrow
max_lng = 0.071722 # Barking ting
travel_mode = 'transit' #'walking'
map_type = 'local' # local or global
N=20

pickle_path = 'data_mode{}_map{}_N{}.p'.format(travel_mode, map_type, N)

import pickle
def draw_map(map_type_, home_lat=0, home_lng=0, N=0, 
			 max_lat=51.612907, min_lat=51.373126, 
			 max_lng=-0.496954, min_lng=0.071722, 
			 travel_mode_='walking'):
	pickle_path = 'data_mode{}_map{}_N{}.p'.format(travel_mode_, map_type_, N)
	if os.path.exists(pickle_path):
		print('Reading in from pickled file...')
		travel_data = pickle.load(open(pickle_path, 'rb'))
		return travel_data[0], travel_data[1], travel_data[2]
	if map_type_ == 'local':
	    lats, lngs = mf.local_grid(home_lat, home_lng, N)
	elif map_type == 'global':
	    lats, lngs = mf.max_grid(N, max_lat, min_lat, max_lng, min_lng)
	else: 
		raise ValueError('Map type must be either "local" or "global"')
	mf.draw_map(home_lat, home_lng, lats, lngs)
	travel_times = mf.retrieve_travel_times(API_key, home_lat, home_lng,
						                      lats, lngs,
						                      mode=travel_mode)
	pickle.dump([lats, lngs, travel_times], open(pickle_path, 'wb'))
	return lats, lngs, travel_times

lats, lngs, travel_times = draw_map(map_type, home_lat, home_lng, N, max_lat, min_lat, max_lng, min_lng)

cutoff_mins = [0,5,10,15,20,30,60, 90, 120]
binned_coords = mf.bin_coords(lats, lngs, travel_times, cutoff_mins)

mf.plot_coords.show()
	 



# def plot_bin(binned_coords_, bin_val):
#     plt.scatter(binned_coords_[bin_val][:,0], binned_coords_[bin_val][:,1])


# #%% Define folium maps
# m = folium.Map(location=[home_lat, home_lng], zoom_start=10)
# feature_group = folium.FeatureGroup("Locations")

# for lat, lng, minute in foo:
#     if minute < 30:
#         feature_group.add_child(folium.Marker(location=[lat,lng]))
# m.add_child(feature_group)
# m.save(os.path.join(os.getcwd(), 'folium_map.html'))








