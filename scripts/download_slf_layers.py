from osgeo import gdal

gdal.UseExceptions()


def get_wmts_uri(
    wmts_url: str, layer_name: str, tile_matrix_set_id: str, style: str
) -> str:
    return f"WMTS:{wmts_url},layer={layer_name},TileMatrixSet={tile_matrix_set_id},Style={style}"


def load_source(uri: str) -> gdal.Dataset:
    return gdal.Open(uri)


def download_layer(source: gdal.Dataset, outfile: str, resample_factor=10):
    gt = source.GetGeoTransform()
    original_xRes = gt[1]  # Pixel width
    original_yRes = abs(gt[5])  # Pixel height (absolute value)

    xRes = original_xRes * resample_factor
    yRes = original_yRes * resample_factor

    gdal.Translate(
        outfile,
        source,
        xRes=xRes,
        yRes=yRes,
        callback=gdal.TermProgress_nocb,
    )


download_config = {
    # SLF Avalanche Terrain Hazard (ATH)
    # "ath": {
    #     "wmts_url": "https://map.slf.ch/WMTSCapabilities.public.xml",
    #     "layer_name": "ch.slf.terrainclassification-hom",
    #     "tile_matrix_set_id": "2056",
    #     "style": "default",
    # },
    # SLF Classified Avalanche Terrain (CAT) SLF
    "cat": {
        "wmts_url": "https://map.slf.ch/WMTSCapabilities.public.xml",
        "layer_name": "ch.slf.terrainclassification-hybr",
        "tile_matrix_set_id": "2056",
        "style": "default",
    },
}

resample_factor = 10
base_dir = "data"


def main():
    for layer_name, source in download_config.items():
        uri = get_wmts_uri(**source)
        dataset = load_source(uri)
        outfile_name = f"{base_dir}/{layer_name}-{resample_factor}.tif"
        download_layer(dataset, outfile_name, resample_factor)


if __name__ == "__main__":
    main()
