from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from src.backend.db import get_all_subscriptions, update_last_alert_sent
from src.backend.fetch_data import fetch_realtime_aurora_data
from src.backend.nearest_neighbour import find_nearest_coord
from src.backend.notifier import send_notification


def check_aurora_alerts():
    aurora_points = fetch_realtime_aurora_data()
    subs = get_all_subscriptions()

    for sub in subs:
        nearest_point, _ = find_nearest_coord([sub.latitude, sub.longitude], aurora_points)
        intensity = nearest_point[2]

        if intensity >= sub.threshold:
            send_notification(email=sub.user_email, name=sub.user_name, city=sub.city, aurora_value=intensity)
            update_last_alert_sent(sub.id, datetime.utcnow())


scheduler = BackgroundScheduler()
scheduler.add_job(check_aurora_alerts, "interval", minutes=15)
scheduler.start()
