# List of file paths to the GeoTIFF files
from pathlib import Path

import rasterio
import rasterio.merge

data_dir = "../data/tiles"
here = Path(__file__).parent
tiff_paths = (here / data_dir).glob("*.tif")
output_file = here / "../data/terrain.tif"


# Load the GeoTIFF files and merge them into a single file
def merge_tiffs(tiff_paths):
    datasets = [rasterio.open(path) for path in tiff_paths]
    rasterio.merge.merge(datasets, dst_path=str(output_file))


def main():
    merge_tiffs(tiff_paths)


if __name__ == "__main__":
    main()
