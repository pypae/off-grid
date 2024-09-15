from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import meshio
import requests
from pyproj import Transformer
from shapely import LineString

from off_grid.pathfinding import Location


def smooth_line(coords: list[Location], tolerance=0.0005):
    """Smooth a ragged shortest path"""
    line = LineString(coords)
    simplified_line = line.simplify(tolerance=tolerance)
    return list(simplified_line.coords)


def convert_lv95_to_wgs84(location: tuple[int, int]) -> tuple:
    # Initialize the transformer: from EPSG:2056 (CH1903+ / LV95) to EPSG:4326 (WGS84)
    transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
    lat, lon = transformer.transform(*location)
    return lat, lon


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
