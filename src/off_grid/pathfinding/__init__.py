# Source: Adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
from off_grid.pathfinding.graph.cat_grid import CATGrid
from off_grid.pathfinding.search.a_star import a_star_search, reconstruct_path
from off_grid.pathfinding.types import Location


def compute_path(start: Location, end: Location) -> list[Location]:
    graph = CATGrid(start, end)
    came_from, _ = a_star_search(graph, start, end)
    shortest_path = reconstruct_path(came_from, start, end)

    # write_mesh_path(graph, shortest_path)

    return shortest_path
