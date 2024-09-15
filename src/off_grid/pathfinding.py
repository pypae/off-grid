# Source: Adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
import heapq
from pathlib import Path

import numpy as np
import rasterio
import rasterio.transform

Location = tuple[int, int]

here = Path(__file__).parent
cat_path = here / "../../data/avi-10.tif"


def compute_centrality_grid(rows: int, cols: int) -> np.ndarray:
    # Compute centrality values for each cell
    center_row = rows / 2
    center_col = cols / 2
    centrality = np.zeros((rows, cols), dtype=np.float32)
    for i in range(rows):
        for j in range(cols):
            # Centrality is higher closer to the center
            centrality[i, j] = 1.0 - (abs(i - center_row) + abs(j - center_col)) / (
                center_row + center_col
            )
    return centrality


def heuristic(
    a: Location,
    b: Location,
    centrality_grid: np.ndarray,
    centrality_weight: float = 1.0,
) -> float:
    (x1, y1) = a
    (x2, y2) = b
    h = abs(x1 - x2) + abs(y1 - y2)  # Manhattan distance
    # Incorporate centrality
    centrality = centrality_grid[x1, y1]
    # Adjust heuristic
    return h - centrality_weight * centrality


def neighbors(pixel: Location, grid: np.ndarray) -> list[Location]:
    (x, y) = pixel
    neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]  # E W N S
    if (x + y) % 2 == 0:
        neighbors.reverse()  # S N W E

    def is_inbounds(pixel: Location) -> bool:
        row, col = pixel
        nrows, ncols = grid.shape
        return 0 <= row < nrows and 0 <= col < ncols

    result = filter(is_inbounds, neighbors)
    return list(result)


def cost(current: Location, next: Location, grid: np.ndarray) -> float:
    row, col = next
    # Ensure indices are within bounds
    nrows, ncols = grid.shape
    if 0 <= row < nrows and 0 <= col < ncols:
        feature = grid[row, col]
        return feature.item()
    else:
        return float("inf")  # Return infinite cost for out-of-bounds


def a_star_search(
    grid: np.ndarray,
    start: Location,
    goal: Location,
    centrality_grid: np.ndarray,
    centrality_weight: float = 1.0,
):
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
                came_from[next] = (current, new_cost)
                priority = new_cost + heuristic(
                    next, goal, centrality_grid, centrality_weight
                )
                heapq.heappush(frontier, (priority, next))

    return came_from


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
        current = came_from[current][0]
    path.reverse()  # optional
    return path


def compute_path(start: Location, end: Location) -> list[Location]:
    with rasterio.open(cat_path) as i:
        cat_data = i.read(1)  # Read the first band
        transform = i.transform
        nrows, ncols = cat_data.shape

    # Compute centrality grid
    centrality_grid = compute_centrality_grid(nrows, ncols)

    # From coordinates, get the pixel units of the start and end points.
    s = rasterio.transform.rowcol(transform, *start)
    e = rasterio.transform.rowcol(transform, *end)

    came_from = a_star_search(cat_data, s, e, centrality_grid)
    shortest_path = reconstruct_path(came_from, s, e)

    # Transform the path from pixel units back to coordinates.
    shortest_path_coords = [
        rasterio.transform.xy(transform, x, y) for x, y in shortest_path
    ]

    return shortest_path_coords
