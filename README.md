# 🌌 AuroraPulse

**Aurora Pulse** is your ultimate companion for chasing the Northern Lights. This web app provides **real-time aurora alerts** based on your location and preferred aurora intensity thresholds, so you never miss a magical aurora display. Catch the aurora before it fades—alerts that keep you in the glow!

Built with **Streamlit**, **Folium**, and **Python**, Aurora Pulse combines geospatial visualization, NOAA aurora data, and personalized notifications to create an intuitive aurora-chasing experience.

---

## ✨ Features

- **Interactive Map:** Click any location on the map to set your aurora alert location.
- **Aurora Intensity Thresholds:** Receive alerts only when aurora intensity meets your chosen threshold.
- **Personalized Notifications:** Get HTML emails addressed to your first name with aurora details.
- **Automated Updates:** Aurora data is fetched automatically from NOAA whenever a request is made and the data is older than 3 hours.
- **Subscription Management:** Save your email, location, and threshold to receive automated alerts.
- **Nearest Aurora Detection:** Finds the closest aurora forecast point to your location using accurate geospatial calculations.
- **Extensible & Modular:** Clean backend structure for fetching data, sending notifications, and database management.

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **Streamlit** for the web UI
- **Folium** for interactive maps
- **SQLite** for storing subscriptions
- **APScheduler** for background jobs (optional)
- **scikit-learn** for nearest-neighbor calculations
- **Loguru** for structured logging
- **NOAA OVATION API** for real-time aurora data
- **SMTP** for sending HTML email notifications

---

## 📦 Project Structure
```
aurora-pulse/
│
├─ main.py # Streamlit app entrypoint
├─ pyproject.toml # Python project and dependencies
├─ aurora_data.json # Cached aurora data
│
├─ src/
│ ├─ backend/
│ │ ├─ db.py # SQLite DB setup & subscription management
│ │ ├─ fetch_data.py # Fetch aurora data & caching
│ │ ├─ nearest_neighbour.py # Distance calculations, threshold checks
│ │ ├─ notifier.py # Email/SMS notifications
│ │ └─ scheduler.py # Background job scheduler (optional)
│
├─ tests/ # Unit tests for all components
├─ Dockerfile # Docker container setup
└─ README.md
```

---

## 🚀 Installation

### Clone the repo:

```bash
git clone https://github.com/yourusername/aurora-pulse.git
cd aurora-pulse
```

### Install dependencies:

```bash
uv sync
```

---

## ⚙️ Configuration
1. Secrets: Copy secrets.toml.template to secrets.toml and fill in your credentials.
```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "<your_secret_here>"
client_id = "<your_google_client_id>"
client_secret = "<your_google_client_secret>"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "<your_email_here>"
app_password = "<your_app_password_here>"
```

2. Aurora Data Cache: aurora_data.json will be automatically created and refreshed when needed.

## 🖥️ Running Locally
```bash
uv run streamlit run main.py
```
Open your browser at http://localhost:8501 to start using the app.

---

## 📬 Notifications

- Aurora alerts are sent as beautifully formatted HTML emails.
- Emails include your first name, selected location, aurora intensity, and tips for observing the Northern Lights.

---

## 🧪 Testing

All components are covered by unit tests:
```bash
uv run pytest tests/ --maxfail=1 -v
```
- tests/test_db.py → Tests DB creation, subscription saving, and alert updates.
- tests/test_fetch_data.py → Tests fetching and parsing aurora data.
- tests/test_notifier.py → Tests email sending and formatting.

---
