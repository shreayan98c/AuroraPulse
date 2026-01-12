import folium
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from loguru import logger
from src.backend.db import save_subscription
from src.backend.fetch_data import load_aurora_points
from src.backend.nearest_neighbour import find_nearest_coord
from src.backend.notifier import send_notification
from src.backend.process_data import check_threshold
from streamlit_folium import st_folium

st.set_page_config(page_title="Aurora Pulse", page_icon="🌌", layout="centered")
st.title("Aurora Chaser 🌌")

# Authentication
if not st.user.is_logged_in:
    if st.button("Log in with Google"):
        st.login()
    st.stop()

if st.button("Log out"):
    st.logout()
st.markdown(f"Welcome! {st.user.name}")


# Optional: show user info + logout
with st.sidebar:
    st.markdown(f"👋 **{st.user.name}**")
    st.markdown(f"📧 {st.user.email}")
    st.button("Log out", on_click=st.logout)

# Reverse geocoder
geolocator = Nominatim(user_agent="aurora_pulse_app")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Session state for user inputs
if "coords" not in st.session_state:
    st.session_state.coords = None
if "city" not in st.session_state:
    st.session_state.city = None
if "toast_shown" not in st.session_state:
    st.session_state.toast_shown = False

if not st.session_state.coords:
    st.caption("📍 Select a location and intensity threshold to get aurora alerts!")

if not st.session_state.coords and not st.session_state.toast_shown:
    st.toast("📍 Select a location and intensity threshold to get aurora alerts!")
    st.session_state.toast_shown = True

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

    location = reverse((clicked_lat, clicked_lng), exactly_one=True, language="en")
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
    st.session_state.toast_shown = False  # Reset toast for new selection
    st.rerun()

if st.session_state.coords:
    if st.session_state.city != "Unknown location":
        st.success(f"Selected Location: {st.session_state.city}")
    else:
        st.warning("Unknown Location selected!")


user_name = st.user.name or "Aurora Chaser"
first_name = user_name.split()[0] if user_name else "Aurora Chaser"
email = st.user.email
threshold = st.number_input("Aurora intensity threshold:", min_value=0, max_value=20, value=8)
if st.button("Check Aurora", disabled=not st.session_state.coords):
    if st.session_state.city and email:
        logger.info(f"Fetching data for {st.session_state.city}...")
        logger.info(f"Coordinates: {st.session_state.coords}")

        save_subscription(
            user_email=email,
            user_name=first_name,
            latitude=st.session_state.coords["lat"],
            longitude=st.session_state.coords["lng"],
            city=st.session_state.city,
            threshold=threshold,
        )
        st.success("Subscription saved! You will get email alerts automatically.")

        aurora_points = load_aurora_points("aurora_data.json")
        nearest_point, distance_km = find_nearest_coord(
            target_coord=[
                st.session_state.coords["lat"],
                st.session_state.coords["lng"],
            ],
            coord_list=aurora_points,
        )

        nearest_lat, nearest_lon, aurora_value = nearest_point
        logger.info(
            f"Nearest aurora data point at ({nearest_lat}, {nearest_lon}) with value {aurora_value}, distance {distance_km:.2f} km"
        )
        st.write(f"Aurora intensity forecast: {aurora_value}")

        if check_threshold(aurora_value, threshold):
            st.write(f"🌌 Nearest aurora point:\n- Distance: {distance_km:.1f} km\n- Aurora intensity: {aurora_value}")
            send_notification(email=email, name=first_name, city=st.session_state.city, aurora_value=aurora_value)
            st.success("Aurora alert sent! Check your email 🌟")
        else:
            st.info("Aurora below threshold. No notification sent.")
    else:
        st.warning("Please enter both city and email.")
