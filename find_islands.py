### trying to cluster points based on a Euclidean distance
## it's a local map so the latitude and longitude is based on the lat and lng multipliers
lat_multiplier=0.002
lng_multiplier=0.003
x = np.linspace(home_lat - (int(N/2)*lat_multiplier), home_lat + (int(N/2)*lat_multiplier), N)
y = np.linspace(home_lng - (int(N/2)*lng_multiplier), home_lng + (int(N/2)*lng_multiplier), N)
lat_difference = round(x[1] - x[0], 6) # 6 decimal places is down to 10cm of accuracy
lng_difference = round(y[1] - y[0], 6)

euc_distance = (lat_difference**2 + lng_difference**2)**0.5 + 0.000005 # euclidean distance/radius for a point
coords = binned_coords[3]

def build_island(coords_, island_, island_index_, euclidean_distance_, neighbours_exist_):
	if island_index_ >= len(island_):
		neighbours_exist_ = False
		return island_, neighbours_exist_
	coords_ = np.asarray([i for i in coords_ if (i == island_[island_index_]).all() != True ]) # remove island element we are examining from coords
	coord_dif = coords_ - island_[island_index_]
	neighbours = coords_[(coord_dif[:,0]**2 + coord_dif[:,1]**2)**0.5 <= euclidean_distance_]
	if neighbours.size == 0:
		neighbours_exist_ = False		
	else:
		island_ = np.append(island_, neighbours, axis=0) 
	print(neighbours_exist_, neighbours, len(coords_))
	return island_, neighbours_exist_

# classify the first coordinate as an island
neighbours_exist = True
island = [coords[0]] # put in list so we can append other elements along the 0 axis
island_index = 0

## now we iterate this over successive elements in the island until no more elements can be added
while neighbours_exist == True:
	island, neighbours_exist = build_island(coords, island, island_index, euc_distance, neighbours_exist)
	island = np.unique(island, axis=0)
	island_index += 1
print(island)

coords = np.array([x for x in set(tuple(x) for x in A) ^ set(tuple(x) for x in B)]) # remove island coords from list of coords






island_list = []
island_list.append(island)

#### for testing
test_island(coords)
test_island(island)
plt.scatter(island[island_index][0], island[island_index][1])
