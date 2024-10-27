from pathlib import Path

import numpy as np
import rasterio

here = Path(__file__).parent
in_path = here / "../data/cat-10.tif"
out_path = here / "../data/ncat-10.tif"

expected_colors = np.array(
    [
        (0, 0, 0, 0),  # Transparent, no avalanche danger
        (244, 243, 124, 192),  # Light yellow, 3+ avalanche runout
        (124, 215, 251, 192),  # Light blue, avalanche runout, remote trigger low
        (50, 143, 252, 192),  # Dark blue, avalanche runout, remote trigger medium
        (247, 147, 191, 192),  # Pink, trigger potential 0.1
        (240, 128, 82, 192),  # Orange, trigger potential 0.25
        (220, 43, 43, 192),  # Red, trigger potential 0.5
        (114, 0, 0, 192),  # Dark red, trigger potential 1.0
        (104, 104, 104, 192),  # Gray, extreme terrain, > 50 degree
        (50, 50, 50, 192),  # Dark gray, extreme terrain, > 60 degree
    ]
)


costs = np.array(
    [
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
)


def color_to_category(data: np.ndarray) -> np.ndarray:
    rgba_data = np.transpose(data, (1, 2, 0)).reshape(-1, 4)

    # Compute the Euclidean distance between each pixel and the expected colors
    distances = np.linalg.norm(rgba_data[:, None] - expected_colors[None, :], axis=2)

    # Find the index of the closest color for each pixel
    closest_color_indices = np.argmin(distances, axis=1)

    # Get the cost each the color / category
    pixel_costs = costs[closest_color_indices]

    # Reshape the result back to the original shape
    discrete_cat = pixel_costs.reshape(data.shape[1], data.shape[2])

    return discrete_cat


def main():
    with rasterio.open(in_path) as i:
        cat_data = i.read()
        metadata = i.meta.copy()

    discrete_cat = color_to_category(cat_data)
    metadata.update(
        dtype=rasterio.uint16,
        count=1,  # Number of bands, as we're saving only the indices
        compress="lzw",
    )

    with rasterio.open(out_path, "w", **metadata) as o:
        o.write(discrete_cat.astype(rasterio.uint16), 1)  # Write to the first band


if __name__ == "__main__":
    main()
