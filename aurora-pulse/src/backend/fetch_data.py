import json

import requests
from loguru import logger

API_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"


def get_city_coordinates(city_name):
    """
    Stub function: Replace with real geocoding API.
    Returns (latitude, longitude) tuple or None.
    """
    fake_coords = {"Reykjavik": (64.1466, -21.9426), "Oslo": (59.9139, 10.7522), "Stockholm": (59.3293, 18.0686)}
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


# make a get request to https://services.swpc.noaa.gov/json/ovation_aurora_latest.json to get the latest aurora data


def fetch_realtime_aurora_data():
    """
    Fetch real aurora data from NOAA API.
    Returns the aurora oval data.
    """
    logger.info("Fetching realtime aurora data from NOAA API...")

    response = requests.get(API_URL)
    if response.status_code == 200:
        with open("aurora_data.json", "w") as f:
            f.write(response.text)
            logger.info("Aurora data fetched and saved successfully.")
        return response.json()
    else:
        logger.error(f"Failed to fetch aurora data: {response.status_code}")
        return None


def load_aurora_points(filepath="aurora_data.json"):
    """
    Returns list of [lat, lon, intensity]
    """
    with open(filepath, "r") as f:
        data = json.load(f)

    points = []
    for lon, lat, intensity in data["coordinates"]:
        points.append([lat, lon, intensity])

    return points
