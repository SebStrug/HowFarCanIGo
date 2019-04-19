# -*- coding: utf-8 -*-
"""Create map showing how far you can get in certain amounts of time"""

#%%
###########
#### SETUP
###########

# Imports, set up api key and client key
import googlemaps
from gmplot import gmplot
import datetime as dt
import json
import time
import random
import geopy.distance
import matplotlib.pyplot as plt
import pandas as pd
import math

# File location to save files
os.chdir("C:\\Users\\Sebastian\\Desktop\\GitHub\\HowFarCanIGo\\")
# Find API key
with open(os.getcwd()+"\\api_key.txt", 'r+') as f:
    API_key = f.readline()
# Set up client key
gmaps = googlemaps.Client(key=API_key)

#%%

# Set date and time as 22nd October 2018 (Monday), 9am
departure_time = dt.datetime.strptime("2018-11-19-09-00", '%Y-%m-%d-%H-%M')
tme = departure_time.time()
date = departure_time.date()
print(date, tme) 

# Retrieve latitude and longitude of my house
home_string = "50 Mount Pleasant Road, W5 1SQ, London, England"
home_loc = gmaps.geocode(home_string)  
home_lat = home_loc[0]["geometry"]["location"]["lat"]
home_lng = home_loc[0]["geometry"]["location"]["lng"]
home_coords = zip([home_lat, home_lng])
print(home_string, home_lat, home_lng)

#%%
######################
#### FUNCTIONS
######################
# Returns travel time to location, using google maps API
# travel_mode = "walking", "transit"
def travel_time_to_loc(origin, destination, travel_mode, departure_time_):
    # get the directions to the location
    directions_result = gmaps.directions(origin, destination, mode = travel_mode, departure_time=departure_time_)
    # return the duration of the overall travel time
    timeNumber = directions_result[0]["legs"][0]["duration"]["value"]
    time_parse = time.strftime("%H:%M:%S", time.localtime(timeNumber)) # return a sensible output
    hours_parse = int(time.strftime("%H", time.localtime(timeNumber))) # return hours
    mins_parse = int(time.strftime("%M", time.localtime(timeNumber))) # return minutes
    secs_parse = int(time.strftime("%S", time.localtime(timeNumber)))
    return directions_result, timeNumber, time_parse, hours_parse, mins_parse, secs_parse

# Creates a lattice of points centred around an origin location
# Create a lattice made of 2N points on a google map centred around my house
def create_lattice(N, lat_multiplier, lng_multiplier, origin_lat, origin_lng):
    lattice_lats = []*N
    lattice_lngs = []*N
    for i in range(-N,N):
        for j in range(-N,N):
            lattice_lats.append(origin_lat + (i*lat_multiplier))
            lattice_lngs.append(origin_lng + (j*lng_multiplier))
    return lattice_lats, lattice_lngs

def calculate_coords(dest_lats, dest_lngs, origin_lat, origin_lng, travel_mode, departure_time, cutoff_time_):
    # Want to save places that are less than our cutoff time in a new list
    good_coords = []    
    for lat, lng in zip(dest_lats, dest_lngs):  
        directions, duration_dt, duration_str, duration_hrs, duration_mins, duration_secs = travel_time_to_loc((origin_lat, origin_lng), (lat, lng), travel_mode, departure_time)
        if dt.timedelta(seconds = duration_dt) < cutoff_time_:
            good_coords.append((lat,lng))
    return [i[0] for i in good_coords], [i[1] for i in good_coords] #return as list of lats and lngs

# Saves the directions to an output file
def save_directions(file, directions):
    with open(file, 'w') as f:
        json.dump(directions, f, ensure_ascii=False, indent=4, sort_keys=True)
        
def clockwiseangle_and_distance(origin, point):
    refvec = [0,1]
    # Vector between point and the origin: v = p - o
    vector = [point[0]-origin[0], point[1]-origin[1]]
    # Length of vector: ||v||
    lenvector = math.hypot(vector[0], vector[1])
    # If length is zero there is no angle
    if lenvector == 0:
        return -math.pi, 0
    # Normalize vector: v/||v||
    normalized = [vector[0]/lenvector, vector[1]/lenvector]
    dotprod  = normalized[0]*refvec[0] + normalized[1]*refvec[1]     # x1*x2 + y1*y2
    diffprod = refvec[1]*normalized[0] - refvec[0]*normalized[1]     # x1*y2 - y1*x2
    angle = math.atan2(diffprod, dotprod)
    # Negative angles represent counter-clockwise angles so we need to subtract them 
    # from 2*pi (360 degrees)
    if angle < 0:
        return 2*math.pi+angle, lenvector
    # I return first the angle because that's the primary sorting criterium
    # but if two vectors have the same angle then the shorter distance should come first.
    return angle, lenvector

#%%
######################
#### TEST SPACE
#######################
## distance between two lat/long coords
#coords_1 = (52.2296756, 21.0122287)
#coords_2 = (52.2296767, 21.0122302)
#print("Distance in m between two coords: ", geopy.distance.distance(coords_1, coords_2).m)

# 9 points of lat = 1 metre?
# 15 points of long = 1 metre?

# string input into directions
#directions, duration_dt, duration_str, duration_hrs, duration_mins, duration_secs = travel_time_to_loc(home_string, "Marble arch station", "transit", departure_time)

# save directions to file
#save_directions("data.txt", directions)

#%%
######################
#### SCATTER MAP
######################  
# Set parameters
N = 10
# obtained multipliers just by testing what's a sensible distance
lat_multiplier = 0.001
lng_multiplier = 0.0015

# Define a cut off time past which we ignore a result
hours_cutoff = 0
minute_cutoff = 15
cutoff_time = dt.timedelta(minutes = minute_cutoff, hours = hours_cutoff)

# generate lattice of points centred around my house
lattice_lats, lattice_lngs = create_lattice(N, lat_multiplier, lng_multiplier, home_lat, home_lng)
# call the google API to see which points I can reach in a set amount of time walking
good_lats, good_lngs = calculate_coords(lattice_lats, lattice_lngs, home_lat, home_lng, "walking", departure_time, cutoff_time)

#%%
# get a boundary of points

# start with the last lat, lng
coords = list(zip(good_lats, good_lngs))
clockwise_coord_list = [[coords[-1][0], coords[-1][1]]]

worst_angle  = 2*math.pi
clockwise_coord = clockwise_coord_list[0]
clockwise_index = -1

for coord_index, coord in enumerate(coords[:-1]): #iterate through coords skipping last point (the starting point)
    angle_to_point, lenvector = clockwiseangle_and_distance(clockwise_coord_list[0], coord)
    print(angle_to_point)
    if angle_to_point < worst_angle:
        worst_angle = angle_to_point
        clockwise_coord = coord
        clockwise_index = coord_index
clockwise_coord_list.append(clockwise_coord)
# now repeat this loop until we're back at the beginning


print(clockwise_coord_list)






#print(list(sorted(coords, key=clockwiseangle_and_distance)))

#%%
# Initialise a map with its centre at my house
gmap = gmplot.GoogleMapPlotter(home_lat, home_lng, 16, API_key) #16 is the zoom level
gmap.marker(home_lat, home_lng, 'cornflowerblue') # not working to plot a marker at my house?#gmap.scatter(lattice_lats, lattice_lngs, color='black', size=3, marker=False) #plot the lats
gmap.scatter(good_lats, good_lngs, color='red', size=10, marker=False) # plot the lngs

           
#gmap.polygon(good_lats, good_lngs, fill_color='blue')

gmap.draw(file_location + "my_map.html") #, map_styles=map_styles)

