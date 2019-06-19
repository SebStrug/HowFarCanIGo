import os
import googlemaps
import folium
import numpy as np
import datetime as dt
import requests
import polyline

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

# Draw map
def draw_map(home_lat, home_lng, lat_list, lng_list):
    """ 
    Draw map as html page

    Generates map of London around origin address with given points

    :param map_type: 'local' or 'global' (see max_grid and local_grid)
    :param home_lat: latitude of origin address
    :param home_lng: longitude of origin address
    :param lat_list: list of destination latitudes
    :param lng_list: list of destination longitudes
    :return: None
    """

    m = folium.Map(location=[home_lat, home_lng])
    feature_group = folium.FeatureGroup("Locations")
    for lat, lng in zip(lat_list, lng_list):
        feature_group.add_child(folium.Marker(location=[lat, lng]))
    m.add_child(feature_group)
    m.save(os.path.join(os.getcwd(), 'folium_map.html'))
    return

def max_grid(N, max_lat, min_lat, max_lng, min_lng):
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
    # # How can I turn it from a grid into a circle?? -> do I want to??
    # x0 = (max(x) - min(x))/2 + min(x)
    # y0 = (max(y) - min(y))/2 + min(y)
    # r = np.sqrt((xv - x0)**2 + (yv - y0)**2)
    # xv[r < (max(x) - min(x))/2] = 9999
    # yv[r < (max(y) - min(y))/2] = 9999
    return xv.flatten(), yv.flatten()

def local_grid(home_lat_, home_lng_, N, lat_multiplier=0.002, lng_multiplier=0.003):
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
    date_today = dt.date.today()
    if date_today.weekday() == 5:
        date_today += dt.timedelta(days=2)
    elif date_today.weekday() == 6:
        date_today += dt.timedelta(days=1)
    departure = dt.datetime.combine(date_today, dt.time(9))
    print('Departure date and time: ', departure.date(), departure.time()) 
    # api takes in time in seconds from epoch
    return str(int((departure-dt.datetime(1970,1,1)).total_seconds()))

def retrieve_travel_times(API_key, home_lat_, home_lng_,
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

    def _build_url(lats_subset, lngs_subset):
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
    assert (len(destination_lats)/100).is_integer(), 'Total number of coordinates must be divisible by 100, number of coordinates is {}'.format(N)
    # we are limited to 100 requests per api so must split up our coordinates
    lats_list = np.split(destination_lats, len(destination_lats)//100)
    lngs_list = np.split(destination_lngs, len(destination_lngs)//100)
    # loop over coordinates to retrieve all data
    all_travel_times = [] 
    for chunk in range(len(lats_list)):
        data = _build_url(lats_list[chunk], lngs_list[chunk])
        travel_times = [elements['duration']['value'] for elements in data['rows'][0]['elements']]
        all_travel_times = np.concatenate((all_travel_times, travel_times))
    assert len(destination_lats) == len(all_travel_times), 'Different number of coordinates ({}), to travel times ({})'.format(len(destination_lats), len(all_travel_times))
    return all_travel_times

def bin_coords(lats_, lngs_, travel_times_, cutoff_mins_):
    """
    Bin coordinates into groups using cut off times

    Coordinates are separated by travel times. For example coordinates may be split into buckets of coordinates that 
    take 0-5 mins, 5-10mins, etc. time to travel to, using whatever mode was provided.

    :param lats_: list of latitude coordinates of destinations
    :param lngs_: list of longitude coordinates of destinations
    :param travel_times_: list of times taken to arrive at each coordinate pair
    :param cutoff_mins_: list of cutoff times

    :return: dictionary of coordinates associated up to each cutoff-time
    """

    def _make_dict_cumulative(dictionary_):
        """
        Makes each key in dictionary contain all values in previous key
        :param dictionary_: dict with a list at each key
        :return: dict with each key containing list containing all values of previous keys
        """
        for key in dictionary_.keys():
            original_key = key
            while key > min(dictionary_.keys()):
                key -= 1
                dictionary_[original_key] = np.concatenate((dictionary_[original_key], dictionary_[key]))
        return dictionary_

    # convert seconds to minutes for travel time
    travel_times_mins = [round(i/60, 1) for i in travel_times_]
    # bin the data
    inds = np.digitize(travel_times_mins, np.array(cutoff_mins_))
    # initialise an empty dictionary
    ttime_dict = dict.fromkeys(np.unique(inds))

    # numpy array of lats and lngs together
    lat_lng = np.asarray(list(zip(lats_,lngs_)))
    for ind in np.unique(inds):
        # find indices of each bin, and apply a mask
        bin_mask = np.where(inds==ind)[0]
        bin_lat_lng = lat_lng[bin_mask]
        ttime_dict[ind] = bin_lat_lng

    return _make_dict_cumulative(ttime_dict)

def plot_coords(binned_coords, cutoff_mins):
    """
    Plot coords with travel time areas

    Plot the list of coordinates with no map, using the travel times to shade areas appropriately.

    :param binned_coords: dictionary of travel time indices with coordinates attached to them
    :param cutoff_mins: list of cutoff times in minutes
    """
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
    return fig
