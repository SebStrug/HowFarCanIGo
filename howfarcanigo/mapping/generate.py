import os
import numpy as np
import datetime as dt
import requests
import polyline
import folium
import time

"""
TO DO


"""

def next_best_date():
    """
    Finds the next datetime which is a weekday, with a time of 9am

    Returns:
        (string): datetime from epoch in seconds as string
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

def retrieve_travel_times(destination_lats, destination_lngs, \
                            API_key, travel_mode_, origin_lat, origin_lng, \
                            departure_time=next_best_date()):
    """
    Retrieves time taken to travel to destination coordinates

    Args:
        destination_lats (list): destination latitudes
        destination_lngs (list): destination longitudes
        API_key (string): API key for googlemaps client
        travel_mode_ (string): 'transit' or 'walking'
        origin_lat (double): origin latitude
        origin_lng (double): origin longitude
        departure_time (string): datetime object from epoch converted to string, time to begin travelling

    Returns:
        destination_lats (numpy array): destination latitudes that can be travelled to
        destination_lngs (numpy array): destination longitudes that can be travelled ot
        travel_times (numpy array): travel times to each coordinate
    """

    def _build_url(lats_subset, lngs_subset):
        """
        Builds url used to retrieve data from google distancematrix api

        Args:
            lats_subset (list): chunk of 100 latitude coordinates
            lngs_subseet (list): chunk of 100 longitude coordinates

        Returns:
            json file containing API data
        """
        # base url for calling distance/time google api    
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
        # add in the origin
        url += "origins=" + str(origin_lat) + "," + str(origin_lng)
        # add in the destination with polyline encoding
        url += "&destinations=enc:" + polyline.encode(
                [(lat,lng) for lat,lng in zip(lats_subset, lngs_subset)],5) + ":"
        url += "&key=" + API_key
        url += "&mode=" + travel_mode_
        url += "&departure_time=" + departure_time
        return requests.get(url).json()

    # this 100 value is used later to multiply the chunks -> use variable instead?
    assert len(destination_lats) == len(destination_lngs), \
        print('Number of latitude coordinates must equal number of longitude coordinates')
    assert (len(destination_lats)**2/100).is_integer(), \
        print('Total number of coordinates must be divisible by 100, number of coordinates is {}'.format(len(destination_lats**2)))

    # we are limited to 100 requests per api so must split up our coordinates
    lats_list = np.split(destination_lats, len(destination_lats)//100)
    lngs_list = np.split(destination_lngs, len(destination_lngs)//100)

    # loop over coordinates to retrieve all data
    all_travel_times = []
    all_bad_indices = []
    for chunk in range(len(lats_list)):
        data = _build_url(lats_list[chunk], lngs_list[chunk])
        print('Chunk index: ', chunk, ' status: ', data['status'])
        if chunk % 50 == 0 and chunk != 0:
            time.sleep(20); print('Sleeping for 20s to prevent API timeout')

        travel_times = []
        bad_indices = []
        for index, element in  enumerate(data['rows'][0]['elements']):
            if element['status'] != 'OK': # some areas are inaccessible (e.g. parts of Heathrow airport, Area 51)
                print(lats_list[chunk][index], lngs_list[chunk][index], element)
                print('bad chunk index: {}'.format(index + chunk*100)) # return the string of this bad lat/lng with the api if we want
                bad_indices.append(index + chunk*100) # must save bad indices to remove them later
            else:
                travel_times.append(element['duration']['value'])
        all_bad_indices = np.concatenate((all_bad_indices, np.asarray(bad_indices)))
        all_travel_times = np.concatenate((all_travel_times, np.asarray(travel_times)))

    # delete elements with a bad status, as no information was returned for these
    destination_lats = np.delete(destination_lats, np.asarray(all_bad_indices))
    destination_lngs = np.delete(destination_lngs, np.asarray(all_bad_indices))  

    assert len(all_travel_times) == len(destination_lats), \
        print('Different number of travel times to destination coordinates')

    return destination_lats, destination_lngs, all_travel_times

def generate_points(map_type_, N,
                    origin_coords, global_coords,
                    lat_multiplier=0.002, lng_multiplier=0.003):
    """ 
    Generates destination coordinates to travel to for map

    Args:
        API_key (string): googlemaps api_key
        map_type_ (string): 'local' or 'global' (see draw_local_grid and draw_local_grid subfuncs)
        N (int): N**2 is the number of destination coordinates desired
        origin_coords (dict): origin coordinates
        global_coords (dict): maximum and minimum coordinates if generating a global map
        lat_multipler (double): distance separator for latitude for the local grid
        lng_multiple (double): distance separator for longitude for the local grid

    Returns:
        (numpy array): latitudes of destinations to travel to
        (numyp array): longitudes of destinations to travel to
    """

    def draw_local_grid(origin_lat, origin_lng):
        """
        Return a lattice of N**2 points around origin coordinates

        Args:
            origin_lat (double): latitude of origin
            origin_lng (double): longitude of origin

        Returns:
            (numpy array): x coordinates
            (numpy array): y coordinates
        """
        x = np.linspace(origin_lat - (int(N/2)*lat_multiplier), origin_lat + (int(N/2)*lat_multiplier), N)
        y = np.linspace(origin_lng - (int(N/2)*lng_multiplier), origin_lng + (int(N/2)*lng_multiplier), N)
        xv, yv = np.meshgrid(x, y)
        return xv.flatten(), yv.flatten()

    def draw_global_grid(max_lat, min_lat, max_lng, min_lng):
        """
        Return a N**2 lattice for maximum/minimum coordinates given

        Args:
            max_lat (double): maximum latitude
            min_lat (double): minimum latitude
            max_lng (double): maximum longitude
            min_lng (double): minimum longitude

        Returns:
            (numpy array): x coordinates
            (numpy array): y coordinates
        """

        # find a grid of points
        x = np.linspace(min_lat, max_lat, N)
        y = np.linspace(min_lng, max_lng, N)
        xv, yv = np.meshgrid(x, y)
        return xv.flatten(), yv.flatten()

    if map_type_ == 'local':
        destination_lats, destination_lngs = draw_local_grid(**origin_coords)
    elif map_type_ == 'global':
        destination_lats, destination_lngs = draw_global_grid(**global_coords)
    else: 
        raise ValueError('Map type must be either "local" or "global"')

    return destination_lats, destination_lngs

if __name__ == "__main__":
    pass
    """ Perform unit testing here

    Need to add main folder to path otherwise will have issues import config
    for unit test
    """