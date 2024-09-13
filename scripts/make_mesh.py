from pathlib import Path

import meshio
import numpy as np
import rasterio
from pydelatin import Delatin

here = Path(__file__).parent
terrain_file = here / "../data/terrain.tif"
output_file = here / "../data/mesh.vtk"


def main():
    print("Creating mesh")
    terrain_data = rasterio.open(terrain_file)
    terrain = terrain_data.read(1)
    tin = Delatin(terrain, max_error=30)  # We're using the first band.
    vertices, triangles = tin.vertices, tin.triangles

    cells = [("triangle", triangles)]
    mesh = meshio.Mesh(vertices, cells)
    mesh.write(str(output_file))


if __name__ == "__main__":
    main()
