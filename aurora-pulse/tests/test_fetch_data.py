import json
import os
from unittest.mock import patch

import pytest
from src.backend import fetch_data

TEST_FILE = "test_aurora.json"


@pytest.fixture
def sample_data():
    data = {
        "coordinates": [
            [0, -90, 2],
            [0, -89, 0],
            [0, -88, 3],
        ]
    }
    with open(TEST_FILE, "w") as f:
        json.dump(data, f)
    yield
    os.remove(TEST_FILE)


def test_load_aurora_points(sample_data):
    points = fetch_data.load_aurora_points()
    assert len(points) == 65160  # Total points in sample data
