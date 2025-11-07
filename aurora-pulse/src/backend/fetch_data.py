def get_city_coordinates(city_name):
    """
    Stub function: Replace with real geocoding API.
    Returns (latitude, longitude) tuple or None.
    """
    fake_coords = {
        "Reykjavik": (64.1466, -21.9426),
        "Oslo": (59.9139, 10.7522),
        "Stockholm": (59.3293, 18.0686)
    }
    return fake_coords.get(city_name)


def fetch_aurora_data(coords):
    """
    Stub function: Replace with aurora API call.
    Returns a forecast aurora intensity (0-10 scale).
    """
    lat, lon = coords
    # Fake logic for demo
    intensity = int((lat + 90) % 10 + 1)
    return intensity
