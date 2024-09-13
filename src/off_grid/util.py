from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import meshio
import requests
from pyproj import Transformer
from shapely import LineString

from off_grid.pathfinding.graph.altitude_mesh import SwissTopoMesh
from off_grid.pathfinding.types import Location


def write_mesh_path(graph: SwissTopoMesh, shortest_path: list[Location]):
    """
    Helper to export the shortest path as a vtk mesh
    that can then be viewed together with the source mesh (e.g. in ParaView)
    for debugging purposes.
    """
    neighbors = graph.graph[shortest_path[0]]
    points = []
    lines = []
    i = 0
    for point in shortest_path[1:]:
        d, h, data = neighbors[point]
        if data is not None:
            points.append(data)
            lines.append((i, i + 1))
            i += 1

        neighbors = graph.graph[point]

    cells = [("line", lines)]
    mesh = meshio.Mesh(points, cells)

    here = Path(__file__).parent
    output_file = here / "path.vtk"
    mesh.write(str(output_file))


def smooth_line(coords: list[Location], tolerance=0.001):
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
