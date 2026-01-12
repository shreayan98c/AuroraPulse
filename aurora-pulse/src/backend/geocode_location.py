from geopy.geocoders import Nominatim
from loguru import logger

# Initialize Nominatim API with a user agent
geolocator = Nominatim(user_agent="city_coordinate_finder")


def get_city_coordinates(city_name):
    """
    Get the latitude and longitude of a city using geopy.
    Args:
        city_name (str): Name of the city to geocode.
    Returns:
        tuple: (latitude, longitude) or None if not found.
    """

    # Geocode the city
    location = geolocator.geocode(city_name)

    # Extract and print the coordinates
    if location:
        logger.info(f"Found coordinates for {city_name}: ({location.latitude}, {location.longitude})")
        latitude = location.latitude
        longitude = location.longitude
        logger.info(f"The coordinates of {city_name} are:")
        logger.info(f"Latitude: {latitude}")
        logger.info(f"Longitude: {longitude}")
        return (latitude, longitude)
    else:
        logger.warning(f"Could not find coordinates for {city_name}.")
        return None
