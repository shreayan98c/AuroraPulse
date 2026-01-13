import folium
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from loguru import logger
from src.backend.db import get_all_subscriptions, save_subscription
from src.backend.fetch_data import load_aurora_points
from src.backend.nearest_neighbour import check_threshold, find_nearest_coord
from src.backend.notifier import send_notification
from src.frontend.style import set_background
from streamlit_folium import st_folium

st.set_page_config(page_title="Aurora Pulse", page_icon="🌌", layout="centered")
st.title("Aurora Chaser 🌌")
set_background("assets/aurora_bg.jpg")


# Authentication
if not st.user.is_logged_in:
    if st.button("Log in with Google"):
        st.login()
    st.stop()

user_name = st.user.name or "Aurora Chaser"
first_name = user_name.split()[0] if user_name else "Aurora Chaser"
email = st.user.email

st.markdown(f"Welcome, {first_name}!")

user_subs = [sub for sub in get_all_subscriptions() if sub.user_email == st.user.email]

# Show user info + logout
with st.sidebar:
    st.markdown(f"👋 **{st.user.name}**")
    st.markdown(f"📧 {st.user.email}")
    st.button("Log out", on_click=st.logout)

    if user_subs:
        st.header("Your Subscriptions 📬")
        for sub in user_subs:
            with st.expander(f"{sub.city} (Threshold: {sub.threshold})", expanded=False):
                st.write(f"📍 Latitude: {sub.latitude:.2f}, Longitude: {sub.longitude:.2f}")
                st.write(f"⏱ Last Alert Sent: {sub.last_alert_sent or 'Never'}")
                # Optional: Delete subscription
                if st.button(f"❌ Remove {sub.city}", key=sub.id):
                    # call remove_subscription(sub.id)
                    st.success(f"{sub.city} removed!")
    else:
        st.info("No subscriptions yet. Select a location to start receiving alerts.")

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
zoom = 2

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

    folium.Marker(
        location=center, popup=popup_text, icon=folium.CustomIcon("assets/aurora_icon.png", icon_size=(30, 30))
    ).add_to(m)

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

# # If using KP index
# kp_index = st.slider("Select Aurora Kp Index Threshold", min_value=0, max_value=9, value=5)
# # Convert Kp to OVATION intensity
# kp_to_ovation = {0: 1, 1: 2, 2: 4, 3: 6, 4: 9, 5: 12, 6: 14, 7: 17, 8: 19, 9: 20}
# threshold = kp_to_ovation[kp_index]

threshold = st.slider("Set aurora intensity threshold:", min_value=0, max_value=20, value=8, step=1)
if threshold >= 15:
    st.caption("🔥 High sensitivity: Alerts for intense auroras!")
elif threshold >= 8:
    st.caption("🌌 Moderate sensitivity: Alerts for moderate auroras.")
else:
    st.caption("✨ Low sensitivity: Alerts for any aurora activity.")
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
        st.toast("Subscription saved! You will get email alerts automatically.")

        with st.spinner("Fetching latest aurora data..."):
            aurora_points = load_aurora_points()
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

        if check_threshold(aurora_value, threshold):
            # st.progress(min(aurora_value / 20, 1.0))
            # st.caption(
            #     f"🌌 Nearest aurora point:\n- Distance: {distance_km:.1f} km\n- Aurora intensity: {aurora_value}"
            # )
            st.markdown(
                f"""
            <div style="background-color:#12172b;padding:20px;border-radius:12px;color:#ffffff;">
                <p><strong>Location:</strong> {st.session_state.city}</p>
                <p><strong>Aurora Intensity:</strong> {aurora_value}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
            # st.write(f"🌌 Nearest aurora point:\n- Distance: {distance_km:.1f} km\n- Aurora intensity: {aurora_value}")
            send_notification(email=email, name=first_name, city=st.session_state.city, aurora_value=aurora_value)
            st.toast("Subscription saved!", icon="🌟")
            st.success("Aurora alert sent! Check your email 🌟")
        else:
            st.info("Aurora currently below threshold. You'll receive an email when it rises above your set threshold.")
    else:
        st.warning("Please enter both city and email.")
