import streamlit as st
from src.backend.fetch_data import get_city_coordinates, fetch_aurora_data
from src.backend.process_data import check_threshold
from src.backend.notifier import send_notification

st.title("Aurora Chaser 🌌")

# User input
city = st.text_input("Enter your city:")
email = st.text_input("Enter your email:")

threshold = st.number_input("Aurora intensity threshold:", min_value=0, max_value=20, value=8)

if st.button("Check Aurora"):
    if city and email:
        st.info(f"Fetching data for {city}...")
        
        coords = get_city_coordinates(city)
        if not coords:
            st.error("Could not find coordinates for this city.")
        else:
            aurora_value = fetch_aurora_data(coords)
            st.write(f"Aurora intensity forecast: {aurora_value}")
            
            if check_threshold(aurora_value, threshold):
                send_notification(email, city, aurora_value)
                st.success("Aurora alert sent! Check your email 🌟")
            else:
                st.info("Aurora below threshold. No notification sent.")
    else:
        st.warning("Please enter both city and email.")
