import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

DB_PATH = "aurora_subscriptions.db"  # file will be created in your app folder


# Data model for a subscription
@dataclass
class Subscription:
    id: int
    user_email: str
    user_name: str
    latitude: float
    longitude: float
    city: str
    threshold: int
    last_alert_sent: Optional[datetime]


# DB Setup and utility functions
def init_db():
    """
    Initializes the SQLite database and creates the subscriptions table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            user_name TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            city TEXT,
            threshold INTEGER NOT NULL,
            last_alert_sent TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# Save or update a subscription
def save_subscription(user_email: str, user_name: str, latitude: float, longitude: float, city: str, threshold: int):
    """
    Inserts a new subscription or updates existing one for the same email + location.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if subscription exists
    c.execute(
        "SELECT id FROM subscriptions WHERE user_email=? AND latitude=? AND longitude=?",
        (user_email, latitude, longitude),
    )
    row = c.fetchone()

    if row:
        # Update threshold and name
        sub_id = row[0]
        c.execute(
            """
            UPDATE subscriptions
            SET threshold=?, user_name=?, city=?
            WHERE id=?
            """,
            (threshold, user_name, city, sub_id),
        )
    else:
        # Insert new
        c.execute(
            """
            INSERT INTO subscriptions (user_email, user_name, latitude, longitude, city, threshold)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_email, user_name, latitude, longitude, city, threshold),
        )

    conn.commit()
    conn.close()


# Fetch all subscriptions
def get_all_subscriptions() -> List[Subscription]:
    """
    Fetches all subscriptions from the database.
    Returns a list of Subscription objects.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM subscriptions")
    rows = c.fetchall()
    conn.close()

    subs = []
    for row in rows:
        last_alert = datetime.fromisoformat(row[7]) if row[7] else None
        subs.append(
            Subscription(
                id=row[0],
                user_email=row[1],
                user_name=row[2],
                latitude=row[3],
                longitude=row[4],
                city=row[5],
                threshold=row[6],
                last_alert_sent=last_alert,
            )
        )
    return subs


# Update last alert sent
def update_last_alert_sent(sub_id: int, alert_time: datetime):
    """
    Updates the last_alert_sent timestamp for a subscription.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE subscriptions SET last_alert_sent=? WHERE id=?",
        (alert_time.isoformat(), sub_id),
    )
    conn.commit()
    conn.close()


# Initialize DB on module load
init_db()
