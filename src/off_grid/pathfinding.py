# Source: Adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
import heapq
from pathlib import Path

import numpy as np
import rasterio
import rasterio.transform
import rasterio.windows

Location = tuple[int, int]

here = Path(__file__).parent
cat_path = here / "../../data/ncat-10.tif"


def heuristic(a: Location, b: Location) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def neighbors(pixel: Location, grid: np.ndarray) -> list[Location]:
    (x, y) = pixel
    # All possible moves: N, S, E, W, NE, NW, SE, SW
    neighbors = [
        (x + 1, y),  # East
        (x - 1, y),  # West
        (x, y - 1),  # North
        (x, y + 1),  # South
        (x + 1, y + 1),  # NE
        (x - 1, y - 1),  # SW
        (x + 1, y - 1),  # SE
        (x - 1, y + 1),  # NW
    ]

    def is_inbounds(pixel: Location) -> bool:
        row, col = pixel
        _, nrows, ncols = grid.shape
        return 0 <= row < nrows and 0 <= col < ncols

    result = filter(is_inbounds, neighbors)
    return list(result)


costs = [
    1,
    10,
    20,
    30,
    100,
    200,
    400,
    800,
    5000,
    10000,
]


def cost(current: Location, next: Location, grid: np.ndarray) -> float:
    col, row = next
    features = grid[:, col, row]
    base_cost = costs[features.item()]

    # Determine if the move is diagonal by checking if both row and column changed
    if abs(current[0] - next[0]) == 1 and abs(current[1] - next[1]) == 1:
        return base_cost * 1.14  # Diagonal penalty
    else:
        return base_cost  # Orthogonal move cost


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


def get_window(
    *points: list[tuple[int, int]], border_width: int = 100
) -> rasterio.windows.Window:
    # Unzip the list of points into two separate lists of rows and columns
    rows, cols = zip(*points)

    # Determine the bounds for the window, ensuring to account for the border
    min_row = min(rows) - border_width
    max_row = max(rows) + border_width
    min_col = min(cols) - border_width
    max_col = max(cols) + border_width

    # Ensure no negative values (in case points are near the edge of the image)
    min_row = max(0, min_row)
    min_col = max(0, min_col)

    # Create the window using the calculated bounds
    window = rasterio.windows.Window.from_slices((min_row, max_row), (min_col, max_col))

    return window


def write_window(cat_data, window, original_dataset, output_path):
    # Create a new transform based on the original transform and the window.
    new_transform = original_dataset.window_transform(window)

    # Create a new dataset with the same properties as the original, but with
    # the dimensions and transform of the window.
    profile = original_dataset.profile
    profile.update(
        {"height": window.height, "width": window.width, "transform": new_transform}
    )

    # Write the data to a new file using the updated profile.
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(cat_data * 10)  # Assuming cat_data is a single band array.


def compute_path(start: Location, end: Location) -> list[Location]:
    with rasterio.open(cat_path) as i:
        transform = i.transform
        # From coordinates, get the pixel units of the start and end points.
        s = rasterio.transform.rowcol(transform, *start)
        e = rasterio.transform.rowcol(transform, *end)
        window = get_window(s, e, border_width=100)
        window_transform = i.window_transform(window)
        cat_data = i.read(window=window)
        window_start = rasterio.transform.rowcol(window_transform, *start)
        window_end = rasterio.transform.rowcol(window_transform, *end)

        # write_window(cat_data, window, i, "test.tif")

    came_from, _ = a_star_search(cat_data, window_start, window_end)
    shortest_path = reconstruct_path(came_from, window_start, window_end)

    # Transform the path from pixel units back to coordinates.
    shortest_path = [
        rasterio.transform.xy(window_transform, x, y) for x, y in shortest_path
    ]

    return shortest_path
