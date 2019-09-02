# -*- coding: utf-8 -*-
import pickle
import googlemaps
import seaborn as sns; sns.set()
from mapping import configure, generate, transform, draw

## Add home marker to map, and maybe tube stops, play with having more layers etc.
## Options to pickle those hull arrays since they take so long to generate
## Options to draw map or just generate points
## Test with many, many points

if __name__ == '__main__':
	# Import configuration file
	API_key, origin_string, origin_coords, \
		travel_mode, map_type, global_coords, \
		N, cutoff_mins = configure.read_config()
	print(origin_string, origin_coords['origin_lat'], origin_coords['origin_lng'])
	print(travel_mode, map_type)
	print(global_coords)
	print(N, cutoff_mins)

	# Set up client key
	gmaps = googlemaps.Client(key=API_key)
	# Define what we will call the data
	data_name = '{}_{}map_N{}'.format(travel_mode, map_type, N)

	# Import data if available for specifications
	lats, lngs, travel_times = configure.import_data(data_name)
	if not travel_times.any():
		# If data does not exist, generate points to travel to
		dest_lats, dest_lngs = generate.generate_points(\
									map_type, N, \
									origin_coords, global_coords)
		lats, lngs, travel_times = generate.retrieve_travel_times(\
										dest_lats, dest_lngs, \
										API_key, travel_mode, \
										**origin_coords)
		# Save data to save future API calls
		pickle.dump([lats, lngs, travel_times], \
			open('data/coords/{}.p'.format(data_name), 'wb'))

	# Transform data into concave hull arrays
	grouped_coords = transform.group_coords(lats, lngs, travel_times, cutoff_mins)
	cutoff_hull_arrays = transform.generate_hull_arrays(grouped_coords, num_bins=4)
	transform.describe_cutoffs(cutoff_mins, grouped_coords)

	# Define a colormap. Could also use `draw.pick_random_cmap(len(cutoff_mins))`
	cmap = sns.cubehelix_palette(8, dark=.2, light=.8, reverse=True, as_cmap=True)
	map_object = draw.draw_folium_map(cutoff_hull_arrays, \
										cutoff_mins, cmap, \
										**origin_coords)
	# Save map
	map_object.save('data/{}.html'.format(data_name))
