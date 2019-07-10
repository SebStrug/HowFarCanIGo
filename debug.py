import matplotlib.pyplot as plt
import hulls

def test_scatter(points_list, val):
	"""
	Plot a scatter graph of the points
	"""
	
	plt.scatter(points_list[val][:,0], points_list[val][:,1], label='Cutoff-time: {}'.format(cutoff_mins[val]))
	plt.legend()

def test_island(points):
	plt.scatter(points[:,0], points[:,1])

def test_hull(points_list, val):
	fig, ax = plt.subplots()
	concave_hull = hulls.ConcaveHull(points_list[val])
    # Calculate the concave hull array
	hull_array = concave_hull.calculate()
	ax.fill(hull_array[:,0], hull_array[:,1], color='b', alpha=0.4)
	fig.show()