from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import meshio
import numpy as np
import requests
from pyproj import Transformer
from scipy.interpolate import interp1d
from shapely import LineString

from off_grid.pathfinding import Location


def smooth_line_with_interp(coords: list, kind="cubic"):
    """Smooth a path using interpolation (linear, quadratic, or cubic)"""
    x_coords, y_coords = zip(*coords)

    # Create the parametric variable t for interpolation
    t = np.linspace(0, 1, len(coords))

    # Create interpolation functions
    interp_x = interp1d(t, x_coords, kind=kind)
    interp_y = interp1d(t, y_coords, kind=kind)

    # Interpolate more points along the path
    t_new = np.linspace(0, 1, len(coords) // 5)
    smooth_x = interp_x(t_new)
    smooth_y = interp_y(t_new)

    smooth_coords = list(zip(smooth_x, smooth_y))

    return smooth_coords


def smooth_line(coords: list[Location], tolerance=0.0001):
    """Smooth a ragged shortest path"""
    line = LineString(coords)
    # simplified_line = line.simplify(tolerance=tolerance)
    smooth_line = smooth_line_with_interp(coords)
    return list(smooth_line)


def convert_lv95_to_wgs84(location: Location) -> Location:
    # Initialize the transformer: from EPSG:2056 (CH1903+ / LV95) to EPSG:4326 (WGS84)
    transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
    lat, lon = transformer.transform(*location)
    return lat, lon


def convert_wgs84_to_lv95(location: Location) -> Location:
    # Initialize the transformer: from EPSG:2056 (CH1903+ / LV95) to EPSG:4326 (WGS84)
    transformer = Transformer.from_crs("epsg:4326", "epsg:2056")
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
