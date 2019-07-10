import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import hulls
from sklearn.cluster import DBSCAN

def bin_coords_by_cutoff(lats_, lngs_, travel_times_, cutoff_mins_):
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
                try:
                    dictionary_[original_key] = np.concatenate((dictionary_[original_key], dictionary_[key]))
                except:
                    pass # may not necessarily be one less key
        return dictionary_

    # convert seconds to minutes for travel time
    travel_times_mins = [round(i/60, 1) for i in travel_times_]
    # bin the data
    inds = np.digitize(travel_times_mins, np.array(cutoff_mins_))
    # initialise an empty dictionary
    ttime_dict = dict.fromkeys(np.unique(inds))

    # numpy array of lats and lngs together
    # hulls takes in longitude as the first element, latitude as the second element!!
    lng_lat = np.asarray(list(zip(lngs_, lats_)))
    for ind in np.unique(inds):
        # find indices of each bin, and apply a mask
        bin_mask = np.where(inds==ind)[0]
        bin_lng_lat = lng_lat[bin_mask]
        ttime_dict[ind] = bin_lng_lat

    return _make_dict_cumulative(ttime_dict)

def cumulate_binned_coords(binned_coords, cutoff_mins):
    """
    FUTURE:: Do we want to remove this and just keep it in main?
        Show the cumulative number of points at each cut off time

    :param binned_coords: dictionary of travel time indices with coordinates attached to them
    :param cutoff_mins: list of minutes for the travel times we are interest up to
    """
    print('Number of values associated with each cut-off time:')
    for val in range(1,len(cutoff_mins)):
        print('Cutoff time: ', cutoff_mins[val], ', Number of points: ', len(binned_coords[val]))

def plot_coords(binned_coords, cutoff_mins):
    """
    Plot coords with travel time areas

    Plot the list of coordinates with no map, using the travel times to shade areas appropriately.

    :param binned_coords: dictionary of travel time indices with coordinates attached to them
    :param cutoff_mins: list of cutoff times in minutes
    """
    fig, ax = plt.subplots()
    for val in binned_coords.keys():
        if val == max(binned_coords.keys()): continue
        print('Calculating cut off minute: ', cutoff_mins[val-1])
        # Create the concave hull object
        concave_hull = hulls.ConcaveHull(binned_coords[val])
        # Calculate the concave hull array
        hull_array = concave_hull.calculate()
        try: 
            ax.fill(hull_array[:,0], hull_array[:,1], color='b', alpha=1/len(cutoff_mins))
        except:
            print('No hull array for cutoff minute ', cutoff_mins[val-1])
    return fig

def cluster_points(points_list, max_distance=np.sqrt(2*0.003**2)): #points list e.g. binned_coords[3]
    """
    Clusters points into islands

    Uses the DBSCAN algorithm to group points based on nearest neighbours

    :param points_list: list of coordinates
    :param max_distance: maximum distance past which another point is a separate island
    :return: dictionary of lists where each list is a separate cluster of points
    """
    clustering = DBSCAN(eps=max_distance, min_samples=1).fit(points_list)
    # points labelled as -1 have no cluster
    assert len(clustering.labels_) == len(points_list)
    #plt.scatter(points_list[:,0], points_list[:,1], c=clustering.labels_, cmap='bwr')
    # initialise dictionary of empty lists
    islands = {i: [] for i in set(clustering.labels_)}
    # group clustered coordinates by label
    for index in range(len(points_list)):
        islands[clustering.labels_[index]].append(points_list[index])
    # change each grouping to a numpy array so that we can use slicing etc.
    for key in islands.keys():
        islands[key] = np.asarray(islands[key])
    return islands

def generate_hull_arrays(b_coords, num_bins=-1):
    """
    Generate hull arrays for each island in each cutoff time

    :param b_coords: binned coordinates dictionary return from the generate_binned_coords function
    :param num_bins: the number of bins that we want to process, if not all. Default to all bins

    """
    rng = np.random.RandomState(42) # initialise random state to generate points later
    bins = list(b_coords.keys()) # make dict keys in a list so we don't have to process them all
    if num_bins == -1: num_bins = max(bins)
    cutoff_hull_arrays = [] # initialise empty array to store all hull arrays for this cut off time
    print('\nGenerating hull arrays...')
    for key in bins[0:num_bins]: # take a certain number of bins 
        print('Processing island: ', key, ' of ', num_bins)
        islands = cluster_points(b_coords[key])
        island_hull_arrays = [] # initialise empty array to store all hull arrays for this island
        for point_set in islands.keys():
            if point_set == -1:
                raise ValueError('POINT SET -1')
                continue
            if len(islands[point_set]) < 3: # need at least 3 points to make a hull array
                # generate two very close by points at random so that we can draw a concave hull
                extra_points = 3 - len(islands[point_set]) 
                temp_points = islands[point_set][0] + rng.rand(extra_points,2)*(10**-7) # this gives the nearby points a resolution of ~1m
                hull_array = hulls.ConcaveHull(np.append(islands[point_set], temp_points).reshape((3, 2))).calculate() # append new points and reshape to correct size
            else:
                hull_array = hulls.ConcaveHull(islands[point_set]).calculate()
            island_hull_arrays.append(hull_array)
        cutoff_hull_arrays.append(island_hull_arrays)
    return cutoff_hull_arrays

def add_cutoff_points(map_object, cutoff_points_, layer_name, line_color, fill_color, weight, text):
    """Draw all islands in a cutoff minute set to a folium map object

    :param map_object: folium map object
    :param cutoff_points_: list of numpy arrays containing the concave hull arrays for an island in the cutoff time
    :param layer_name: name of the cutoff layer
    :param line_color: color of the edge of the polygon to draw
    :param fill_color: color of the fill of the polygon to draw
    :param weight: weight of the polygon edge to draw
    :param text: FUTURE:: to remove?
    :return: folium map object
    """
    fg = folium.FeatureGroup(name=layer_name) # create a feature group
    # now add all the polygons in this cutoff time to the feature group
    for island_index, island_points in enumerate(cutoff_points):
        island_points = np.fliplr(island_points) # flip axis so we get long,lat tuple
        fg.add_child(folium.vector_layers.Polygon(locations=island_points, color=line_color, fill_color=fill_color,
                                              weight=weight)) #, popup=(folium.Popup(text)))
        map_object.add_child(fg)
    return(map_object)