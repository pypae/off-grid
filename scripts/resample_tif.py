from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

here = Path(__file__).parent
in_path = here / "../data/avi.tif"  # Input TIFF file path
out_path = here / "../data/avi-10.tif"  # Output TIFF file path


def resample_raster(input_path, output_path, window_size=10, method="average"):
    with rasterio.open(input_path) as src:
        # Read the source metadata
        meta = src.meta.copy()
        transform = src.transform
        data = src.read()  # Read all bands

    # Original dimensions
    bands, rows, cols = data.shape

    # Calculate new dimensions
    new_rows = rows // window_size
    new_cols = cols // window_size

    # Adjust the transform to account for the resampling
    new_transform = transform * Affine.scale(window_size)

    # Update metadata for the output file
    meta.update({"height": new_rows, "width": new_cols, "transform": new_transform})

    # Initialize an array to hold the resampled data
    resampled_data = np.zeros((bands, new_rows, new_cols), dtype=data.dtype)

    for b in range(bands):
        for i in range(new_rows):
            for j in range(new_cols):
                # Define the window boundaries
                row_start = i * window_size
                row_end = row_start + window_size
                col_start = j * window_size
                col_end = col_start + window_size

                # Extract the window
                window = data[b, row_start:row_end, col_start:col_end]

                # Compute the statistic
                if method == "average":
                    resampled_value = window.mean()
                elif method == "max":
                    resampled_value = window.max()
                else:
                    raise ValueError(
                        f"Unknown method '{method}'. Use 'average' or 'max'."
                    )

                # Assign the computed value to the resampled data
                resampled_data[b, i, j] = resampled_value

    # Write the resampled data to the output file
    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(resampled_data)


def main():
    # Choose the resampling method: 'average' or 'max'
    method = "max"  # or 'max'

    # Call the resampling function
    resample_raster(in_path, out_path, window_size=10, method=method)


if __name__ == "__main__":
    main()
