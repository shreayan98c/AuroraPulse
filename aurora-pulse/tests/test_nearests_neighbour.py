import numpy as np
from src.backend import nearest_neighbour as nn


def test_haversine_distance():
    dist = nn.haversine(0, 0, 0, 90)
    assert round(dist, 1) == 10007.5  # quarter Earth circumference ~10,007.5 km


def test_find_nearest_coord():
    coords = [[0, 0, 5], [10, 10, 3], [-5, -5, 7]]
    target = [2, 2]
    nearest, distance = nn.find_nearest_coord(target, coords)
    assert nearest.tolist() == [0, 0, 5]


def test_check_threshold():
    assert nn.check_threshold(5, 3) is True
    assert nn.check_threshold(2, 3) is False
