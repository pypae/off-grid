#!/usr/bin/env bash

gdal_translate \
  "WMTS:https://map.slf.ch/WMTSCapabilities.public.xml,layer=ch.slf.terrainclassification-hom,TileMatrixSet=2056,Style=default" \
  -projwin 2735000 1199000 2740000 1191000 \
  -projwin_srs EPSG:2056 \
  data/ath.tif
