from mapping import generate

API_key, origin_string, origin_coords, \
	travel_mode, map_type, global_coords, \
	N, cutoff_mins = generate.read_config()
print(origin_string, origin_coords['origin_lat'], origin_coords['origin_lng'])
print(travel_mode, map_type)
print(global_coords)
print(N, cutoff_mins)

lats, lngs, travel_times = generate.generate_points(API_key, map_type, N, travel_mode, \
													origin_coords, global_coords, \
													lat_multiplier=0.002, lng_multiplier=0.003)