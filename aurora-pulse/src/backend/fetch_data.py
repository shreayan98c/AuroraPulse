import json

import requests
import streamlit as st
from loguru import logger

API_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"


# make a get request to https://services.swpc.noaa.gov/json/ovation_aurora_latest.json to get the latest aurora data


@st.cache_data(ttl=300)  # cache for 5 minutes
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
    Returns list of [lat, lon, intensity] from NOAA aurora JSON.
    Uses caching to avoid repeated disk reads.
    """
    return _load_aurora_points_cached(filepath)


@st.cache_data(show_spinner=False)
def _load_aurora_points_cached(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    points = []
    for lon, lat, intensity in data["coordinates"]:
        points.append([lat, lon, intensity])

    return points
