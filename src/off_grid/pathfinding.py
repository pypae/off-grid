# Source: Adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
import heapq
from pathlib import Path

import numpy as np
import rasterio
import rasterio.transform

Location = tuple[int, int]

here = Path(__file__).parent
cat_path = here / "../../data/avi.tif"


def heuristic(a: Location, b: Location) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def neighbors(pixel: Location, grid: np.ndarray) -> list[Location]:
    (x, y) = pixel
    neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]  # E W N S
    if (x + y) % 2 == 0:
        neighbors.reverse()  # S N W E

    def is_inbounds(pixel: Location) -> bool:
        row, col = pixel
        _, nrows, ncols = grid.shape
        return 0 <= row < nrows and 0 <= col < ncols

    result = filter(is_inbounds, neighbors)

    return list(result)


def cost(current: Location, next: Location, grid: np.ndarray) -> float:
    col, row = next
    features = grid[:, col, row]
    return features.item()


def a_star_search(grid: np.ndarray, start: Location, goal: Location):
    frontier: list[tuple[float, Location]] = []
    heapq.heappush(frontier, (0, start))
    came_from: dict[Location, tuple[Location | None, float]] = {start: (None, 0)}

    while frontier:
        priority, current = heapq.heappop(frontier)
        cost_so_far = came_from[current][1]

        if current == goal:
            break

        for next in neighbors(current, grid):
            new_cost = cost_so_far + cost(current, next, grid)
            if next not in came_from or new_cost < came_from[next][1]:
                came_from[next] = current, new_cost
                priority = new_cost + heuristic(next, goal)
                heapq.heappush(frontier, (priority, next))

    return came_from, cost_so_far


def reconstruct_path(
    came_from: dict[Location, tuple[Location | None, float]],
    start: Location,
    goal: Location,
) -> list[Location]:
    current: Location | None = goal
    path: list[Location] = []
    if goal not in came_from:  # no path was found
        return []
    while current is not None:
        path.append(current)
        current, cost = came_from[current]
    path.reverse()  # optional
    return path


def compute_path(start: Location, end: Location) -> list[Location]:
    with rasterio.open(cat_path) as i:
        cat_data = i.read()
        transform = i.transform

    # From coordinates, get the pixel units of the start and end points.
    s = rasterio.transform.rowcol(transform, *start)
    e = rasterio.transform.rowcol(transform, *end)

    came_from, _ = a_star_search(cat_data, s, e)
    shortest_path = reconstruct_path(came_from, s, e)

    # Transform the path from pixel units back to coordinates.
    shortest_path = [rasterio.transform.xy(transform, x, y) for x, y in shortest_path]

    return shortest_path
