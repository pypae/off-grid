from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

import meshio
import numpy as np
import rasterio
from affine import Affine
from off_grid.pathfinding.types import Location, Number

here = Path(__file__).parent
mesh_path = here / "../../../../data/mesh_centroids.vtk"
terrain_path = here / "../../../../data/terrain.tif"
cat_path = here / "../../../../data/cat.tif"


Graph = Mapping[Location, Mapping[Location, tuple[Number, Number, Any]]]


def is_inside_triangle(pt: Location, triangle) -> bool:
    """Check if a point pt is inside the triangle using barycentric coordinates."""

    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    v1, v2, v3 = triangle
    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


def interpolate_altitude(
    pt: Location, triangle: list[tuple[float, float, float]]
) -> float:
    """Interpolate the altitude at point pt using the vertices of the triangle and their altitudes."""

    def area(p1, p2, p3):
        return abs(
            (
                p1[0] * (p2[1] - p3[1])
                + p2[0] * (p3[1] - p1[1])
                + p3[0] * (p1[1] - p2[1])
            )
            / 2.0
        )

    v1, v2, v3 = triangle
    z1, z2, z3 = v1[2], v2[2], v3[2]

    total_area = area(v1, v2, v3)
    area1 = area(pt, v2, v3) / total_area
    area2 = area(pt, v3, v1) / total_area
    area3 = area(pt, v1, v2) / total_area

    return z1 * area1 + z2 * area2 + z3 * area3


def build_graph(
    mesh: meshio.Mesh,
    transform: Affine,
    get_data,
    additional_points: list[Location] | None = None,
) -> Graph:
    graph: Graph = defaultdict(dict)

    # We only have triangles, no quads or similar.
    for triangle in mesh.cells_dict["triangle"]:
        transformed_triangle = []
        # Extract the three points of the triangle
        for i in range(3):
            # Current point
            p1 = mesh.points[triangle[i]]

            # Next point in the triangle
            p2 = mesh.points[triangle[(i + 1) % 3]]

            # Apply the affine transform to the x, y coordinates
            x1, y1 = transform * (p1[0], p1[1])
            x2, y2 = transform * (p2[0], p2[1])

            # Calculate the distance between the two points (ignoring altitude)
            distance = np.linalg.norm([x2 - x1, y2 - y1])
            altitude_diff = p2[2] - p1[2]

            # Add the edge to the graph (in both directions)
            graph[(x1, y1)][(x2, y2)] = distance, altitude_diff, p1, get_data(p1)
            graph[(x2, y2)][(x1, y1)] = distance, -altitude_diff, p2, get_data(p2)

            transformed_triangle.append((x1, y1, p1[2]))

        if not additional_points:
            continue

        new_additional_points = additional_points[:]
        for p in additional_points:
            if is_inside_triangle(p, transformed_triangle):
                altitude = interpolate_altitude(p, transformed_triangle)

                # Add the additional point to the graph, connecting it to each vertex of the triangle
                for vertex in transformed_triangle:
                    # Calculate distance and altitude difference between the additional point and the vertex
                    distance_to_vertex = np.linalg.norm(
                        [p[0] - vertex[0], p[1] - vertex[1]]
                    )
                    altitude_diff_to_vertex = altitude - vertex[2]

                    # Add the edges to the graph
                    graph[p][vertex[:2]] = (
                        distance_to_vertex,
                        altitude_diff_to_vertex,
                        None,
                    )
                    graph[vertex[:2]][p] = (
                        distance_to_vertex,
                        -altitude_diff_to_vertex,
                        None,
                    )
                # triangles are non-overlapping, so we can remove the additional point now.
                new_additional_points.remove(p)
        additional_points = new_additional_points

    if additional_points:
        raise Exception("Some points are not inside the mesh.")

    return graph


class SwissTopoMesh:
    def __init__(
        self,
        start: Location,
        end: Location,
        uphill_coefficient: float = 10,
        downhill_coefficient: float = 10,
    ):
        mesh = meshio.read(mesh_path)  # TODO build mesh here dynamically, or read it.
        with rasterio.open(terrain_path) as terrain_data:
            transform = terrain_data.transform

        with rasterio.open(cat_path) as cat_file:
            # TODO read classified avalanche terrain data and add the values to the graph
            cat_data = cat_file.read()

        # We invert the y axis because the mesh has the reference point at the top left,
        # While on the map it's on the bottom left
        inverted_transform = (
            transform
            * Affine.scale(1, -1)
            * Affine.translation(0, -terrain_data.height)
        )

        self.graph = build_graph(
            mesh,
            inverted_transform,
            cat_data,
            additional_points=[start, end],
        )
        self.uphill_coefficient = uphill_coefficient
        self.downhill_coefficient = downhill_coefficient

    def neighbors(self, id: Location) -> list[Location]:
        result = []
        for id, (distance, altitude_difference, _) in self.graph[id].items():
            if distance == 0:
                continue
            slope = altitude_difference / distance
            if slope > 0.6:
                continue
            result.append(id)
        return result

    def cost(self, from_id: Location, to_id: Location) -> float:
        neighbors = self.graph[from_id]
        distance, altitude_difference, _ = neighbors[to_id]

        # Calculate the slope (incline)
        if distance == 0:  # Avoid division by zero
            return float("inf")

        slope = abs(altitude_difference) / distance

        if altitude_difference > 0:
            # Uphill: Penalize steep inclines exponentially
            cost = abs(altitude_difference) * 1 + slope
        else:
            # Downhill: Penalize steep descents (but typically less severely)
            cost = abs(altitude_difference) * 1 + slope

        return cost


if __name__ == "__main__":
    # Segneshütte: 2'737'317.79, 1'192'300.47
    start = (2737300, 1192300)

    # Piz Segnas: 2'737'202.55, 1'196'779.22
    end = (2737200, 1196800)
    mesh = SwissTopoMesh(start, end)
    neighbors = mesh.neighbors(start)
    print(neighbors)
    for neighbor in neighbors[:1]:
        subns = mesh.neighbors(neighbor)
        for subn in subns:
            print(mesh.cost(neighbor, subn))
