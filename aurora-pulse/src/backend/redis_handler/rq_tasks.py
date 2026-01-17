from datetime import datetime, timedelta

from loguru import logger
from src.backend.config import KP_TO_OVATION
from src.backend.db import get_all_subscriptions, update_last_alert_sent
from src.backend.fetch_data import fetch_realtime_aurora_data
from src.backend.nearest_neighbour import find_nearest_coord
from src.backend.notifier import send_notification

MIN_ALERT_GAP = timedelta(hours=1)  # avoid spam


def check_aurora_alerts():
    """
    Background task:
    - Fetch latest aurora data (cached)
    - Check all subscriptions
    - Send alerts if thresholds met
    """
    logger.info("RQ task started: checking aurora alerts")

    aurora_data = fetch_realtime_aurora_data()
    if not aurora_data:
        logger.warning("No aurora data available")
        return

    subs = get_all_subscriptions()
    logger.info(f"Checking {len(subs)} subscriptions")

    for sub in subs:
        nearest_point, _ = find_nearest_coord([sub.latitude, sub.longitude], aurora_data["coordinates"])

        intensity = nearest_point[2]
        kp_threshold = sub.threshold
        ovation_threshold = KP_TO_OVATION.get(kp_threshold)
        if ovation_threshold is None:
            logger.warning(f"Invalid threshold {kp_threshold} for subscription {sub.id}")
            continue

        logger.debug(f"Subscription {sub.id}: intensity={intensity}, ovation_threshold={ovation_threshold}")
        if intensity >= ovation_threshold:
            now = datetime.now()

            if sub.last_alert_sent and now - sub.last_alert_sent < MIN_ALERT_GAP:
                continue

            send_notification(
                email=sub.user_email,
                name=sub.user_name,
                city=sub.city,
                aurora_value=kp_threshold,
            )

            update_last_alert_sent(sub.id, now)
            logger.success(f"Alert sent to {sub.user_email}")

    logger.info("RQ task completed")
