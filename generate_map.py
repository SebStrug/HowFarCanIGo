import os
import numpy as np
import datetime as dt
import requests
import polyline
import pickle
import folium
import time

def retrieve_home_address():
    """
    Reads home address from file

    Reads local file in folder where the first line is a string with the home address
    If a second line exists, it contains the latitude and longitude separated by a comma

    :return: home address string, home latitude, home longitude
    """
    with open(os.getcwd()+"\\home_address.txt","r+") as f:
        home_string = f.readline()
        home_coords = f.readline()
        f.close()  
        # if the file doesn't have home_coords
        if home_coords == '': 
            print('Calling google api for home address')
            home_info = gmaps.geocode(home_string) 
            home_lat = home_info[0]['geometry']['location']['lat']
            home_lng = home_info[0]['geometry']['location']['lng']
        else:    
            home_lat = float(home_coords.split(',')[0])
            home_lng = float(home_coords.split(',')[1])
    return home_string, home_lat, home_lng

def draw_max_grid(N, max_lat, min_lat, max_lng, min_lng):
    """
    Return a lattice of points for all of London

    Calculates a square lattice, with the number of points input into the function for London,
    given minimum and maximum latitudes and longitudes

    :param N: number of points along one axis of lattice, total number of points in lattice will be N**2
    :param max_lat: maximum latitude desired
    :param min_lat: minimum latitude desired
    :param max_lng: maximum longitude desired
    :param min_lng: minimum longitude desired.
    :return: list of latitudes and list of longitudes
    """

    # find a grid of points
    x = np.linspace(min_lat, max_lat, N)
    y = np.linspace(min_lng, max_lng, N)
    xv, yv = np.meshgrid(x, y)
    return xv.flatten(), yv.flatten()

def draw_local_grid(home_lat_, home_lng_, N, lat_multiplier, lng_multiplier):
    """
    Return a lattice of points around origin coordinates

    Returns a list of N**2 points around the origin address

    :param home_lat_: latitude of origin address
    :param home_lng_: longitude of home address
    :param N: number of points along one axis of lattice, total number of points in lattice is N**2
    :param lat_multiplier: effective spacing of latitude points -> how many m^2 does default value correspond to?
    :param lng_multiplier: effective spacing of longitude points
    """
    x = np.linspace(home_lat_ - (int(N/2)*lat_multiplier), home_lat_ + (int(N/2)*lat_multiplier), N)
    y = np.linspace(home_lng_ - (int(N/2)*lng_multiplier), home_lng_ + (int(N/2)*lng_multiplier), N)
    xv, yv = np.meshgrid(x, y)
    return xv.flatten(), yv.flatten()

def next_best_date():
    """
    Finds next best datetime to use

    Finds the next datetime which is a weekday, where the time is 9am

    :return: datetime object for 9am on the next nearest datetime
    """
    date_today = dt.datetime.today()
    if date_today.hour > 9:
        date_today += dt.timedelta(days=1)
    if date_today.weekday() == 5:
        date_today += dt.timedelta(days=2)
    elif date_today.weekday() == 6:
        date_today += dt.timedelta(days=1)
    departure = dt.datetime.combine(date_today, dt.time(9))
    print('Departure date and time: ', departure.date(), departure.time()) 
    # api takes in time in seconds from epoch
    return str(int((departure-dt.datetime(1970,1,1)).total_seconds()))

def retrieve_travel_times(API_key, N, home_lat_, home_lng_,
                          destination_lats, destination_lngs,
                          mode='transit'):
    """
    Retrieves data from the google distance matrix api
    :param API_key: personal google api key
    :param home_lat_: float latitude of origin
    :param home_lng_: float longitude of origin
    :param destination_lats: list of latitude floats of destinations
    :param destination_lats: list of longitude float of destinations
    :param mode: mode of travelling e.g. walking, transit
    :return: list of travel times to each latitude/longitude pair in seconds
    """

    def _build_url(lats_subset, lngs_subset, mode):
        """
        Builds url used to retrieve data from google distancematrix api
        :param lats_subset: chunk of 100 latitude coordinates
        :param lngs_subset: chunk of 100 longitude coordinates
        :return: json file containing data
        """
        # base url for calling distance/time google api    
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
        # add in the origin
        url += "origins="+str(home_lat_)+","+str(home_lng_)
        # add in the destination with polyline encoding
        url += "&destinations=enc:"+polyline.encode(
                [(lat,lng) for lat,lng in zip(lats_subset, lngs_subset)],5) + ":"
        url += "&key="+API_key
        url += "&mode="+mode
        url += "&departure_time="+departure_time
        return requests.get(url).json()

    departure_time = next_best_date()
    # this 100 value is used later to multiply the chunks -> use variable instead?
    assert (len(destination_lats)**2/100).is_integer(), ('Total number of coordinates must be divisible by 100, number of coordinates is {}'.format(N**2))
    # we are limited to 100 requests per api so must split up our coordinates
    lats_list = np.split(destination_lats, len(destination_lats)//100)
    lngs_list = np.split(destination_lngs, len(destination_lngs)//100)
    # loop over coordinates to retrieve all data
    all_travel_times = [] 
    all_bad_indices = []
    for chunk in range(len(lats_list)):
        data = _build_url(lats_list[chunk], lngs_list[chunk], mode)
        print('Chunk index: ', chunk, ' status: ', data['status'])
        if chunk % 50 == 0 and chunk != 0:
            time.sleep(20); print('Sleeping for 20s...')
        travel_times = []
        bad_indices = []
        for index, element in  enumerate(data['rows'][0]['elements']):
            if element['status'] != 'OK': # some areas are inaccessible via walking (places in Heathrow airport)
                print(lats_list[chunk][index], lngs_list[chunk][index], element)
                # can return the string of this bad lat/lng with the api if we want
                print('bad chunk index: {}'.format(index + chunk*100))
                bad_indices.append(index + chunk*100)
            else:
                travel_times.append(element['duration']['value'])
        all_bad_indices += bad_indices
        all_travel_times = np.concatenate((all_travel_times, travel_times))
    # delete elements with a bad status, as no information was returned for these
    destination_lats = np.delete(destination_lats, np.asarray(all_bad_indices))
    destination_lngs = np.delete(destination_lngs, np.asarray(all_bad_indices))  
    print(len(destination_lats), len(all_travel_times))
    return destination_lats, destination_lngs, all_travel_times

def generate_points(API_key, map_type_, home_lat=0, home_lng=0, N=0, 
             max_lat=51.612907, min_lat=51.373126, 
             max_lng=-0.496954, min_lng=0.071722, 
             lat_multiplier=0.002, lng_multiplier=0.003,
             travel_mode_='walking'):
    """ 
    Draw map as html page

    Generates map of London around origin address with given points

    :param map_type_: 'local' or 'global' (see max_grid and local_grid)
    :param home_lat: latitude of origin address if using local map
    :param home_lng: longitude of origin address if using local map
    :param max_lat: maximum latitude used if using global map
    :param min_lat: minimum latitude used if using global map
    :param max_lng: maximum longitude used if using global map
    :param min_lng: minimum longitude used if using global map
    :param travel_mode: type of travel used "walking" or "transit"
    :return: list of latitudes, list of longitudes, list of travel times to each coord pair
    """

    # define a path for either reading data from or writing to, to save future google api calls
    pickle_path = 'data_mode{}_map{}_N{}.p'.format(travel_mode_, map_type_, N)
    if os.path.exists(pickle_path):
        print('Reading in from pickled file...')
        travel_data = pickle.load(open(pickle_path, 'rb')) # load in data if it exists
        return travel_data[0], travel_data[1], travel_data[2]
    if map_type_ == 'local':
        lats, lngs = draw_local_grid(home_lat, home_lng, N, lat_multiplier=lat_multiplier, lng_multiplier=lng_multiplier)
    elif map_type_ == 'global':
        lats, lngs = draw_max_grid(N, max_lat, min_lat, max_lng, min_lng)
    else: 
        raise ValueError('Map type must be either "local" or "global"')
    # find times using api for how long it takes to travel to each coordinate pair
    lats, lngs, travel_times = retrieve_travel_times(API_key, N, home_lat, home_lng,
                                                      lats, lngs,
                                                      mode=travel_mode_)
    pickle.dump([lats, lngs, travel_times], open(pickle_path, 'wb'))
    return lats, lngs, travel_times

def describe_cutoffs(cutoff_mins, binned_coords):
    """Print how many points are associated with each area of time

    :param list cutoff_mins: time in minutes for each cutoff
    :param dictionary binned_coords: points grouped with each cutoff index
    :returns: None
    """
     
    print('Number of values associated with each cut-off time:')
    for val in range(1,len(cutoff_mins)):
        try:
            print('Cutoff time: ', cutoff_mins[val], ', Number of points: ', len(binned_coords[val]))
        except: 
            pass