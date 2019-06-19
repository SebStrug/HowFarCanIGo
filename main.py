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

# Date and time must be current or in the future for the api
departure = mf.next_best_date()
print('Departure date and time: ', departure.date(), departure.time()) 
# google distance api takes a departure time in seconds since epoch
departure_s = str(int((departure-datetime.datetime(1970,1,1)).total_seconds()))
# information about home address
home_string, home_lat, home_lng = mf.home_address()
print(home_string, home_lat, home_lng)

# Grid of points based on maximum latitude/longitude. N is number of points in grid.
# N must be a multiple of 10 to split it later
N = 50
lats, lngs = mf.max_grid(50)
lats, lngs = mf.local_grid(home_lat, home_lng, 50)

mf.draw_map(home_lat, home_lng, lats, lngs)
travel_times = mf.retrieve_travel_times(API_key, 
					  home_lat, home_lng,
                      lats, lngs,
                      departure_s,
                      mode='walking')

cutoff_mins = [0,5,10,15,20,30,60, 90, 120]
binned_coords = mf.bin_coords(lats, lngs, travel_times, cutoff_mins)

# now we need to find an edge to each of these so we can shade them appropriately
# make the mpl plot (no fill yet)
fig, ax = plt.subplots()
for val in binned_coords.keys():
	print('Calculating cut off minute: ', cutoff_mins[val-1])
	# Create the concave hull object
	concave_hull = hulls.ConcaveHull(binned_coords[val])
	# Calculate the concave hull array
	hull_array = concave_hull.calculate()
	try: 
		ax.fill(hull_array[:,0], hull_array[:,1], color='b', alpha=0.2)
	except:
		print('No hull array for cutoff minute ', cutoff_mins[val-1])
fig.show()
	 



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








