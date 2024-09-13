from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine
from matplotlib import pyplot as plt
from off_grid.pathfinding.types import Location
from rasterio.transform import rowcol
from scipy.spatial import KDTree

here = Path(__file__).parent
cat_path = here / "../../../../data/cat.tif"


class ClassifiedAvalanceTerrain:
    expected_colors = np.array(
        [
            (0, 0, 0, 0),  # Transparent, no avalanche danger
            (244, 243, 124, 192),  # Light yellow, 3+ avalanche runout
            (124, 215, 251, 192),  # Light blue, avalanche runout, remote trigger low
            (50, 143, 252, 192),  # Dark blue, avalanche runout, remote trigger medium
            # TODO: Dark blue, avalanche runout, remote trigger high
            (247, 147, 191, 192),  # Pink, trigger potential 0.1
            (240, 128, 82, 192),  # Orange, trigger potential 0.25
            (220, 43, 43, 192),  # Red, trigger potential 0.5
            (114, 0, 0, 192),  # Dark red, trigger potential 1.0
            (104, 104, 104, 192),  # Gray, extreme terrain, > 50 degree
            (50, 50, 50, 192),  # Dark gray, extreme terrain, > 60 degree
        ]
    )

    def __init__(self, cat_path):
        with rasterio.open(cat_path) as cat_file:
            self.cat_data = cat_file.read()
            self.bounds = cat_file.bounds
            self.transform = cat_file.transform

    def get_cat_data(self, location: Location):
        x, y = location
        col, row = rowcol(self.transform, x, y)
        rgba_color = self.cat_data[:, col, row]

        # Calculate the Euclidean distance between the current color and all expected colors
        distances = np.linalg.norm(self.expected_colors - rgba_color, axis=1)

        # Find the index of the closest color
        closest_color_index = np.argmin(distances)

        return closest_color_index

    def _plot_color_distribution(self):
        # Extract colors and counts for plotting
        colors = list(self.color_counts.keys())
        counts = list(self.color_counts.values())

        # Convert RGBA to normalized RGB for matplotlib
        normalized_colors = [tuple(np.array(color[:3]) / 255) for color in colors]

        # Plot a bar chart of color distribution
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(colors)), counts, color=normalized_colors)
        plt.xticks(
            range(len(colors)),
            [f"Color {i+1}" for i in range(len(colors))],
            rotation=45,
        )
        plt.ylabel("Count")
        plt.title("Distribution of Mapped Colors")
        plt.show()

        # Plot color patches for each color
        plt.figure(figsize=(10, 2))
        for i, color in enumerate(colors):
            plt.fill_between([i, i + 1], 0, 1, color=normalized_colors[i])
            plt.text(
                i + 0.5,
                0.5,
                str(color),
                ha="center",
                va="center",
                fontsize=10,
                color="black",
            )
        plt.xlim(0, len(colors))
        plt.yticks([])
        plt.title("Mapped Colors")
        plt.show()


class CATGrid:
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

    def __init__(self, start: Location, end: Location):
        self.cat = ClassifiedAvalanceTerrain(cat_path)
        # self.cat._plot_color_distribution()

    def _inbounds(self, id: Location):
        x, y = id
        left, bottom, right, top = self.cat.bounds
        if x < left or x > right:
            return False
        if y < bottom or y > top:
            return False
        return True

    def neighbors(self, id: Location) -> list[Location]:
        (x, y) = id
        neighbors = [(x + 10, y), (x - 10, y), (x, y - 10), (x, y + 10)]  # E W N S
        if (x + y) % 2 == 0:
            neighbors.reverse()  # S N W E

        result = filter(self._inbounds, neighbors)
        return list(result)

    def cost(self, from_id: Location, to_id: Location) -> float:
        try:
            cat = self.cat.get_cat_data(to_id)
        except IndexError:
            return float("inf")

        cost = self.costs[cat]
        return cost


if __name__ == "__main__":
    # Segneshütte: 2'737'317.79, 1'192'300.47
    start = (2737300, 1192300)

    # start = (2737287.42, 1194509.72)

    # Piz Segnas: 2'737'202.55, 1'196'779.22
    end = (2737200, 1196800)
    grid = CATGrid(start, end)
    neighbors = grid.neighbors(start)
    print(neighbors)
    for neighbor in neighbors:
        print(grid.cost(start, neighbor))
