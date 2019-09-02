import matplotlib.pyplot as plt
import folium
import matplotlib
import seaborn as sns; sns.set()
import random
import numpy as np

def add_cutoff_points(map_object, cutoff_points_, layer_name, line_color, fill_color, weight, text=''):
    """
    Draw all islands in a cutoff minute set to a folium map object

    Args:
        (folium map object): containing overall map
        cutoff_points_ (list): numpy arrays containing the concave hull arrays for an island in the cutoff time
        layer_name (str): name of the cutoff layer
        line_color (str): color of the edge of the polygon to draw
        fill_color (str): color of the fill of the polygon to draw
        weight (int): weight of the polygon edge to draw
        text (str): description of layer, defaults to blank

    Returns:
        (folium map object): generated map
    """
    fg = folium.FeatureGroup(name=layer_name) # create a feature group
    # now add all the polygons in this cutoff time to the feature group
    for island_index, island_points in enumerate(cutoff_points_):
        if island_points is None: continue
        island_points = np.fliplr(island_points) # flip axis so we get long,lat tuple
        fg.add_child(folium.vector_layers.Polygon(locations=island_points, color=line_color, fill_color=fill_color,
                                              weight=weight)) #, popup=(folium.Popup(text)))
        map_object.add_child(fg)
    return map_object

def draw_folium_map(cutoff_hull_arrays_, cutoff_mins_, cmap, origin_lat, origin_lng):
    """
    Draw the map as a html object using folium

    Args:
        data_name (str): Name by which we call this map/data
        cutoff_hull_arrays_ (list): list of list containings points as concave hulls
        cutoff_mins_ (list): cutoff minute integers
        cmap (cmap object): colormap used to shade in the map
        origin_lat (double): latitude of origin
        origin_lng (double): longitude of origin

    Returns:
        (folium map object): generated map
    """

    my_map = folium.Map(location=[origin_lat, origin_lng], zoom_start=11) # Initialize map at origin with zoom level
    # convert RGB to hexcode for folium
    colormap = [matplotlib.colors.rgb2hex(cmap(i)[:3]) for i in range(cmap.N)][::4]
    for cutoff_index, cutoff_points in enumerate(cutoff_hull_arrays_):
        if cutoff_index == len(cutoff_hull_arrays_)-1: continue # skip last one as this is jsut all points
        add_cutoff_points(my_map, cutoff_points, layer_name='Cutoff {} mins'.format(cutoff_mins_[cutoff_index+1]),
                                    line_color='black' # colormap[cutoff_index] may work
                                    ,fill_color=colormap[cutoff_index], weight=1)
    folium.LayerControl(collapsed=False).add_to(my_map) # Add layer control and show map
    return my_map

def pick_random_cmap(num_layers):
    """
    Pick a colormap as random to use in the folium map

    Args:
        num_layers (int): Number of cutoff times, or layers to the map
    Returns:
        (cmap object): colormap
    """
    cmaps = []
    cmaps.append(sns.diverging_palette(250, 15, s=75, l=40, as_cmap=True))
    cmaps.append(sns.color_palette("Paired", n_colors=num_layers+6))
    cmaps.append(sns.dark_palette('yellow', n_colors=5))
    cmaps.append(sns.cubehelix_palette(8, dark=.2, light=.8, reverse=True, as_cmap=True))
    return random.choice(cmaps)

def draw_points(map_object, list_of_points, layer_name, line_color, fill_color, text):
    """FUTURE: IMPROVE, DOCUMENT, MAKE USABLE"""
    fg = folium.FeatureGroup(name=layer_name)
    for point in list_of_points:
        fg.add_child(folium.CircleMarker(point, radius=1, color=line_color, fill_color=fill_color,popup=(folium.Popup(text))))
    map_object.add_child(fg)

def plot_coords(binned_coords, cutoff_mins):
    """
    Plot coords with travel time areas

    Plot the list of coordinates with no map, using the travel times to shade areas appropriately.

    Args:
        binned_coords (dict): travel time indices with coordinates attached to them
        cutoff_mins (list): list of cutoff times in minutes

    Returns:
        (matplotlib fig object)
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

def draw_python_graph(cutoff_hull_arrays_):
    """Draw the map in a Matplotlib graph for convenient display

    Args:
        cutoff_hull_arrays (list): cutoff points as lists of island clusters
    
    Returns:
        (matplotlib fig object
    """

    fig, ax = plt.subplots()
    # loop through points associated with each cut off time
    for cutoff_index, cutoff_points in enumerate(cutoff_hull_arrays_):
        # loop through each island in each cutoff time
        for island_index, island_points in enumerate(cutoff_points):
            if island_points is None: continue
            ax.fill(island_points[:,0], island_points[:,1], color='b', alpha=0.4)
    return fig