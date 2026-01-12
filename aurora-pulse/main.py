import folium
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from loguru import logger
from src.backend.fetch_data import fetch_aurora_data, get_city_coordinates
from src.backend.notifier import send_notification
from src.backend.process_data import check_threshold
from streamlit_folium import st_folium

st.set_page_config(page_title="Aurora Pulse", page_icon="🌌", layout="centered")
st.title("Aurora Chaser 🌌")

# Reverse geocoder
geolocator = Nominatim(user_agent="aurora_pulse_app")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Session state for user inputs
if "coords" not in st.session_state:
    st.session_state.coords = None
if "city" not in st.session_state:
    st.session_state.city = None

if not st.session_state.coords:
    st.info("Click on the map to select your location for aurora alerts!")

# Create map
center = [0, 0]  # default center
zoom = 1

if st.session_state.coords:
    center = [
        st.session_state.coords["lat"],
        st.session_state.coords["lng"],
    ]
    zoom = 10

m = folium.Map(location=center, zoom_start=zoom)

# Add marker on click
if st.session_state.coords:
    popup_text = f"City: {st.session_state.city}" if st.session_state.city else "Selected Location"

    folium.Marker(location=center, popup=popup_text, icon=folium.Icon(color="red", icon="info-sign")).add_to(m)

# Render map
map_data = st_folium(m, width=725, height=400)

# Handle map click
if map_data and map_data["last_clicked"]:
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lng = map_data["last_clicked"]["lng"]
    st.session_state.coords = {"lat": clicked_lat, "lng": clicked_lng}

    location = reverse(f"{clicked_lat}, {clicked_lng}", exactly_one=True, language="en")
    address = location.raw.get("address", {}) if location else {}

    # City fallbacks
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("hamlet")
        or address.get("county")
        or "Unknown location"
    )
    st.session_state.city = city
    st.rerun()

if st.session_state.coords:
    if st.session_state.city != "Unknown location":
        st.success(
            f"Selected Location: {st.session_state.city} ({st.session_state.coords['lat']:.4f}, {st.session_state.coords['lng']:.4f})"
        )
    else:
        st.warning("Unknown Location selected!")


email = "shreayan98c@gmail.com"
threshold = st.number_input("Aurora intensity threshold:", min_value=0, max_value=10, value=8)
if st.button("Check Aurora", disabled=not st.session_state.coords):
    if st.session_state.city and email:
        logger.info(f"Fetching data for {st.session_state.city}...")

        coords = get_city_coordinates(st.session_state.city)
        if not coords:
            st.error("Could not find coordinates for this city.")
        else:
            aurora_value = fetch_aurora_data(coords)
            st.write(f"Aurora intensity forecast: {aurora_value}")

            if check_threshold(aurora_value, threshold):
                send_notification(email, st.session_state.city, aurora_value)
                st.success("Aurora alert sent! Check your email 🌟")
            else:
                st.info("Aurora below threshold. No notification sent.")
    else:
        st.warning("Please enter both city and email.")
