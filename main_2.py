# -*- coding: utf-8 -*-
"""Create map showing how far you can get in certain amounts of time"""

#%%
# Imports, set up api key and client key
import os
import googlemaps
import folium
import datetime as dt
import json
import requests
import polyline
import numpy as np
import datetime

# File location to save files
os.chdir("C:\\Users\\Sebastian\\Desktop\\GitHub\\HowFarCanIGo\\")
# Find API key
with open(os.getcwd()+"\\api_key.txt", 'r+') as f:
    API_key = f.readline()
    f.close()
# Set up client key
gmaps = googlemaps.Client(key=API_key)

#%%
# Initialise base settings for the map

# Define the coords for the maximum cardinal directions we want to look at
max_north = [51.612921,-0.192423]
max_east = [51.526948,0.064606]
max_south = [51.374325,-0.123588]
max_west = [51.515167,-0.490182]
# turn into latitude and longitude lists
max_lats = [max_north[0],max_east[0],max_south[0],max_west[0]]
max_lngs = [max_north[1],max_east[1],max_south[1],max_west[1]]

# Date and time must be current or in the future for the api
departure_time = dt.datetime.strptime("2019-04-22-09-00", '%Y-%m-%d-%H-%M')
# google distance api takes a departure time in seconds since epoch
departure_time_s = str(int((departure_time-datetime.datetime(1970,1,1)).total_seconds()))
tme = departure_time.time()
date = departure_time.date()
print(date, tme) 

# Home address
with open(os.getcwd()+"\\home_address.txt","r+") as f:
    home_string = f.readline()
    home_coords = f.readline()
    f.close()  
home_lat = float(home_coords.split(',')[0])
home_lng = float(home_coords.split(',')[1])
print(home_string, home_lat, home_lng)

#%% Define functions
# Creates a lattice of 2N points centred around an origin location
# obtained multipliers just by testing what's a sensible distance
lat_multiplier = 0.002
lng_multiplier = 0.003
def create_lattice(N, lat_multiplier, lng_multiplier, origin_lat, origin_lng):
    lat_list = []
    lng_list = []
    for i in range(-N,N):
        for j in range(-N,N):
            lat_list.append(origin_lat + (i*lat_multiplier))
            lng_list.append(origin_lng + (j*lng_multiplier))
    return lat_list, lng_list

# Creates a lattice based on the max/min of a set of coords provided
def create_lattice_2(lats, lngs, N):
    # N is the number of intermediary points you want to have
    max_lat = max(max_lats)
    min_lat = min(max_lats)
    max_lng = max(max_lngs)
    min_lng = min(max_lngs)
    lat_list = []; lng_list = []
    for lats in np.linspace(min_lat,max_lat,N+2):
        for lngs in np.linspace(min_lng,max_lng,N+2):
            lat_list.append(lats)
            lng_list.append(lngs)
    return list(lat_list), list(lng_list)

# builds the url to call the distance/time google api
def build_url(home_lat_, home_lng_,
              destination_lats, destination_lngs,
              time = departure_time_s,
              mode = 'transit'):
    #this is the base url for calling distance/time google api    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    #add in the origin
    url += "origins="+str(home_lat_)+","+str(home_lng_)
    #add in the destination with polyline encoding
    url += "&destinations=enc:"+polyline.encode(
            [(lat,lng) for lat,lng in zip(lat_list, lng_list)],5) + ":"
    url += "&key="+API_key
    url += "&mode="+mode
    url += "&departure_time="+time
    return url

#%% Lattice generation
# generate lattice of points centred around my house
#lat_list, lng_list = create_lattice(N, lat_multiplier, lng_multiplier, home_lat, home_lng)

# generate latice of points based on cardinal maximums
N = 6
lat_list, lng_list = create_lattice_2(max_lats, max_lngs, N)

url = build_url(home_lat, home_lng, lat_list, lng_list)

#%%
def travel_time(url):
    response = requests.get(url)
    data = response.json()
    travel_time_list = []
    for elements in data['rows'][0]['elements']:
        travel_time_list.append(elements['duration']['value'])
    return data, travel_time_list

duration_list = travel_time(url)

#%%
duration_list_s = [i%60 for i in duration_list]
foo = zip(lat_list,lng_list,duration_list_s)

#%% Define folium maps
m = folium.Map(location=[home_lat, home_lng], zoom_start=10)
feature_group = folium.FeatureGroup("Locations")

for lat, lng, minute in foo:
    if minute < 30:
        feature_group.add_child(folium.Marker(location=[lat,lng]))
m.add_child(feature_group)
m.save(os.path.join(os.getcwd(), 'folium_map.html'))


# Define a cut off time past which we ignore a result
hours_cutoff = 0
minute_cutoff = 15
cutoff_time = dt.timedelta(minutes = minute_cutoff, hours = hours_cutoff)







