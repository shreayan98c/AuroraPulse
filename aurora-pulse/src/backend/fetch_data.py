import json
import os
import time

import requests
import streamlit as st
from loguru import logger

from .config import API_URL, CACHE_FILE, CACHE_TTL


# @st.cache_data(ttl=300)  # cache for 5 minutes
def fetch_realtime_aurora_data():
    """
    Fetch real aurora data from NOAA API.
    Returns the aurora oval data.
    """
    # Check if cache exists and is recent
    if os.path.exists(CACHE_FILE):
        last_modified = os.path.getmtime(CACHE_FILE)
        age = time.time() - last_modified
        if age < CACHE_TTL:
            logger.info(f"Using cached aurora data ({age / 3600:.2f} hours old).")
            with open(CACHE_FILE, "r") as f:
                return json.load(f)

    # Fetch fresh data from API
    # Make a get request to https://services.swpc.noaa.gov/json/ovation_aurora_latest.json to get the latest aurora data

    logger.info("Fetching realtime aurora data from NOAA API...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
        logger.info("Aurora data fetched and saved successfully.")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch aurora data: {e}")

        # Fallback to cached data if available
        if os.path.exists(CACHE_FILE):
            logger.warning("Using old cached data due to API failure.")
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        return None


def load_aurora_points():
    """
    Returns list of [lat, lon, intensity] from NOAA aurora JSON.
    Uses caching to avoid repeated disk reads.
    """
    data = fetch_realtime_aurora_data()
    if not data:
        return []

    # Convert coordinates to [lat, lon, intensity] format
    points = []
    for lon, lat, intensity in data.get("coordinates", []):
        points.append([lat, lon, intensity])
    return points


# @st.cache_data(show_spinner=False)
def _load_aurora_points_cached(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    points = []
    for lon, lat, intensity in data["coordinates"]:
        points.append([lat, lon, intensity])

    return points
