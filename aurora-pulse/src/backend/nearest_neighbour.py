import numpy as np
from sklearn.neighbors import BallTree


def haversine(lat1, lon1, lat2, lon2) -> float:
    """
    Calculate the great circle distance between two points on the Earth (specified in decimal degrees)

    Parameters:
        lat1, lon1 -- latitude and longitude of point 1
        lat2, lon2 -- latitude and longitude of point 2
    Returns:
        Distance in kilometers between point 1 and point 2
    """
    R = 6371  # Earth radius (km)
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def find_nearest_coord(target_coord, coord_list):
    """
    Find the nearest latitude/longitude pair from a predefined list using BallTree (Haversine distance).

    Parameters:
    target_coord : list or tuple
        Target coordinate as [lat, lon].
    coord_list : array-like
        List or array of coordinates [[lat, lon, ...], ...].
        Extra columns (like IDs or data) are preserved in the result.

    Returns:
    nearest_coord : np.ndarray
        The nearest coordinate row from coord_list.
    distance_km : float
        The great-circle distance in kilometers.
    """
    coords = np.array(coord_list)
    target = np.array(target_coord[:2]).reshape(1, -1)

    # Convert to radians for haversine metric
    coords_rad = np.radians(coords[:, :2])
    target_rad = np.radians(target)

    # Build BallTree
    tree = BallTree(coords_rad, metric="haversine")

    # Query nearest neighbor
    dist, idx = tree.query(target_rad, k=1)

    nearest_coord = coords[idx[0][0]]
    distance_km = dist[0][0] * 6371.0  # convert to km

    return nearest_coord, distance_km


if __name__ == "__main__":
    # Your target coordinate (latitude, longitude)
    target = np.array([0, -85])

    nearest_coord, distance = find_nearest_coord(target, [[10, -80, 5], [0, -86, 10], [-5, -90, 15], [20, -70, 8]])
    print("Nearest coordinate:", nearest_coord)
    print("Distance (km):", distance)
    print("Aurora intensity at nearest coordinate:", nearest_coord[2])
