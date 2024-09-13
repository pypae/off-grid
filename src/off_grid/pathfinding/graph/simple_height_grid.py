from functools import lru_cache
from typing import TypedDict

import requests
from off_grid.pathfinding.types import Location


class HeightResponse(TypedDict):
    height: str


@lru_cache()
def get_height(location: Location) -> float:
    (x, y) = location
    response = requests.get(
        f"https://api3.geo.admin.ch/rest/services/height?easting={x}&northing={y}"
    )
    result: HeightResponse = response.json()
    return float(result["height"])


def calculate_bounding_box(point1: Location, point2: Location, buffer=1000):
    min_easting, max_easting = sorted([point1[0], point2[0]])
    min_northing, max_northing = sorted([point1[1], point2[1]])
    return (
        min_easting - buffer,
        min_northing - buffer,
    ), (
        max_easting + buffer,
        max_northing + buffer,
    )


class SimpleSwissTopoAPIHeightGrid:
    def __init__(self, start: Location, end: Location):
        self.bounding_box = calculate_bounding_box(start, end)

    def _inbounds(self, loc: Location):
        if self.bounding_box is None:
            return True
        (low_x, low_y), (high_x, high_y) = self.bounding_box
        (x, y) = loc
        return x >= low_x and x <= high_x and y >= low_y and y <= high_y

    def neighbors(self, id: Location) -> list[Location]:
        (x, y) = id
        neighbors = [(x + 100, y), (x - 100, y), (x, y - 100), (x, y + 100)]  # E W N S
        if (x + y) % 2 == 0:
            neighbors.reverse()  # S N W E
        result = filter(self._inbounds, neighbors)
        return list(result)

    def cost(self, from_id: Location, to_id: Location) -> float:
        height_diff = get_height(to_id) - get_height(from_id)
        distance = (100**2 + height_diff**2) ** 0.5
        slope = abs(height_diff) / 100
        return distance * slope**2
