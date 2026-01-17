import folium
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from loguru import logger
from rq import Queue
from src.backend.config import KP_TO_OVATION
from src.backend.db import get_all_subscriptions, remove_subscription, save_subscription
from src.backend.fetch_data import load_aurora_points
from src.backend.nearest_neighbour import find_nearest_coord
from src.backend.notifier import send_notification
from src.backend.redis_handler.redis_conn import redis_conn
from src.backend.redis_handler.rq_tasks import check_aurora_alerts
from src.frontend.style import set_background
from streamlit_folium import st_folium

st.set_page_config(page_title="Aurora Pulse", page_icon="🌌", layout="centered")
st.title("Aurora Pulse 🌌")
set_background("assets/aurora_bg.jpg")


# Authentication
if not st.user.is_logged_in:
    if st.button("Log in with Google"):
        st.login()
    st.stop()

q = Queue("aurora", connection=redis_conn)

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
                # Delete subscription
                if st.button(f"❌ Remove {sub.city}", key=sub.id):
                    remove_subscription(sub.id)
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

    # folium.Marker(
    #     location=center, popup=popup_text, icon=folium.CustomIcon("assets/aurora_icon.png", icon_size=(30, 30))
    # ).add_to(m)  # looks a little out of place

    folium.Marker(location=center, popup=popup_text, icon=folium.Icon(color="darkblue", icon="info-sign")).add_to(m)

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

# If using KP index
kp_index = st.slider(
    "Select Aurora Kp Index Threshold",
    min_value=0,
    max_value=9,
    value=5,
    help=(
        "The Kp Index measures global geomagnetic activity on a scale from 0 to 9.\n\n"
        "• 0-2: Quiet geomagnetic conditions\n\n"
        "• 3-4: Minor activity\n\n"
        "• 5+: Geomagnetic storm (auroras visible farther south)\n\n"
        "Higher Kp values mean stronger and more widespread auroras."
    ),
)

if kp_index >= 7:
    st.caption("😍 Strong geomagnetic storm - auroras visible far south!")
elif kp_index >= 5:
    st.caption("📸 Moderate storm - auroras likely at high latitudes")
else:
    st.caption("🔭 Quiet to minor activity - faint auroras possible under dark skies and special equipment")

# Convert Kp to OVATION intensity
threshold = KP_TO_OVATION[kp_index]

# # If using OVATION intensity
# threshold = st.slider("Set aurora intensity threshold:", min_value=0, max_value=20, value=8, step=1)
# if threshold >= 15:
#     st.caption("😍 Alerts for intense auroras visible with naked eyes!")
# elif threshold >= 8:
#     st.caption("📸 Alerts for auroras that can be captured with a camera!")
# else:
#     st.caption("🔭 Alerts for faint auroras visible under dark skies and special equipment!")

if st.button("Check Aurora", disabled=not st.session_state.coords):
    if st.session_state.city and email:
        save_subscription(
            user_email=email,
            user_name=first_name,
            latitude=st.session_state.coords["lat"],
            longitude=st.session_state.coords["lng"],
            city=st.session_state.city,
            threshold=kp_index,
        )

        # Enqueue background job for redis worker
        q.enqueue(
            check_aurora_alerts,
            job_timeout=300,
            result_ttl=0,
        )

        st.toast("✅ Subscription saved! We'll monitor auroras for you 🌌")
        st.success("You're subscribed, alerts will be sent automatically!")
