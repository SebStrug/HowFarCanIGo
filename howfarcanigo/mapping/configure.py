import os
import pickle

def read_config():
    """
    Reads config.py or configExample.py file for inputs to program

    Reads the api key, origin string (or origin lat/long) from the config.py file
    if exists, otherwise reads configExample.py file
    Checks variables read are of correct types

    TODO:
        Is this function too large/needs to be split up?
        Performs relatively simple operations, don't see good way to split it

    Args:
        config_path_ (str): path to config.py file

    Returns:
        api_key (str): API key used in application
        origin_string (str): origin address
        origin_lat (float): origin latitude
        origin_lng (float): origin longitude
    """
    def check_numeric(variables):
        for var in variables:
            assert isinstance(var, (int,float)), "Non-numeric {} provided".format(var)

    try:
        import howfarcanigo.config as config
    except:
        print("Custom configuration file not setup. Using example.")
        print("Plase rename configExample.py to config.py with custom parameters")
        import howfarcanigo.configExample as config

    if config.api_key == "":
        raise ValueError("No API key provided.")

    check_numeric((config.origin_lat, config.origin_lng))

    # if no latitude/longitude provided, must retrieve this information
    if float(config.origin_lat) == 0.0 and float(config.origin_lng) == 0.0:
        print("Calling Google API to retrieve coorindates using origin address")
        origin_info = gmaps.geocode(config.origin_string) 
        config.origin_lat = origin_info[0]['geometry']['location']['lat']
        config.origin_lng = origin_info[0]['geometry']['location']['lng'] 

    origin_coords = {'origin_lat': config.origin_lat, 'origin_lng': config.origin_lng}

    assert config.travel_mode in ("transit", "walking"), \
        "Travel mode must be `transit` or `walking`"
    assert config.map_type in ("global", "local"), \
        "Map type must be `global` or `walking`"

    if config.map_type == "global":
        assert config.max_lat != 0.0 and config.min_lat != 0.0, "Provide global coordinates for a global map"
        assert config.max_lng != 0.0 and config.min_lng != 0.0, "Provide global coordinates for a global map"

    check_numeric((config.max_lat, config.min_lat, config.max_lng, config.min_lng))
    global_coords = {'max_lat': config.max_lat, 'min_lat': config.min_lat, \
                     'max_lng': config.max_lng, 'min_lng': config.min_lng}

    check_numeric([config.N])
    config.N = int(config.N)

    check_numeric(config.cutoff_mins)
    config.cutoff_mins = [int(_) for _ in config.cutoff_mins]
    # first element of cutoff_mins list must be 0 to correctly bin values
    if config.cutoff_mins[0] != 0:
        config.cutoff_mins.insert(0, 0)

    return config.api_key, config.origin_string, \
            origin_coords, config.travel_mode, config.map_type, \
            global_coords, config.N, config.cutoff_mins


def import_data(data_name):
    """
    Import pickled coordinate and travel time data if it exists

    Args:
        data_name (str): name of pickled data

    Return:
        lats (list): destination latitudes
        lngs (list): destination longitudes
        travel_times (list): time taken to trave to each destination coordinate
    """
    
    pickle_path = 'data/coords/{}.p'.format(data_name)
    if os.path.exists(pickle_path):
        # If we already have data pickled, don't generate any more
        print('Reading in from pickled file...')
        lats, lngs, travel_times = pickle.load(open(pickle_path, 'rb')) # load in data if it exists
        return lats, lngs, travel_times
    else:
        return [], [], []