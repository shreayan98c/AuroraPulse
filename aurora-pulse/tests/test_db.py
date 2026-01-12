import os
import sqlite3
from datetime import datetime

import pytest
from src.backend import db

TEST_DB = "test_aurora_subscriptions.db"


@pytest.fixture
def setup_db(monkeypatch):
    # Redirect DB path to test DB
    monkeypatch.setattr(db, "DB_PATH", TEST_DB)
    db.init_db()
    yield
    # Cleanup
    os.remove(TEST_DB)


def test_save_and_fetch_subscription(setup_db):
    db.save_subscription("test@example.com", "TestUser", 12.3, 45.6, "TestCity", 5)
    subs = db.get_all_subscriptions()
    assert len(subs) == 1
    assert subs[0].user_email == "test@example.com"
    assert subs[0].city == "TestCity"
    assert subs[0].threshold == 5


def test_update_last_alert(setup_db):
    # First, insert a subscription
    db.save_subscription("test@example.com", "TestUser", 12.3, 45.6, "TestCity", 5)

    # Fetch it
    subs = db.get_all_subscriptions()
    sub_id = subs[0].id

    now = datetime.now()
    db.update_last_alert_sent(sub_id, now)

    updated_subs = db.get_all_subscriptions()
    assert updated_subs[0].last_alert_sent.isoformat() == now.isoformat()
