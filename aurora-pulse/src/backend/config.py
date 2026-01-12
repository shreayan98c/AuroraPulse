API_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"  # NOAA Aurora API endpoint
CACHE_FILE = "aurora_data.json"  # Local cache file for aurora data
CACHE_TTL = 3 * 60 * 60  # 3 hours in seconds
DB_PATH = "aurora_subscriptions.db"  # TODO: change to external hosted DB in production
