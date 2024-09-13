import folium
import pyinstrument
import streamlit as st
from streamlit_folium import folium_static

from off_grid.pathfinding import compute_path
from off_grid.util import convert_lv95_to_wgs84, get_height, smooth_line


def main():
    st.title("Pathfinding based on Classified Avalanche Terrain Map")

    # Segneshütte: 2'737'317.79, 1'192'300.47
    # start = (2737317.79, 1192300.47)
    start = (2737300, 1192300)

    # Piz Segnas: 2'737'202.55, 1'196'779.22
    end = (2737200, 1196800)

    start_latlon = convert_lv95_to_wgs84(start)
    end_latlon = convert_lv95_to_wgs84(end)

    m = folium.Map(location=start_latlon, zoom_start=12)

    folium.TileLayer(
        tiles="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg",
        attr='&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>',
        name="Winter Basemap",
        overlay=False,
        control=True,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://map.slf.ch/public/mapcache/wmts/1.0.0/ch.slf.terrainclassification-hybr/default/GoogleMapsCompatible/{z}/{y}/{x}.png",
        name="Classified Avalanche Terrain, SLF",
        attr='&copy; <a href="https://www.slf.ch/">SLF</a>',
        overlay=True,
        control=True,
        opacity=0.5,
    ).add_to(m)

    folium.LayerControl().add_to(m)

    folium.Marker(
        location=start_latlon,
        popup=get_height(start),
        tooltip="Start Point",
    ).add_to(m)

    folium.Marker(
        location=end_latlon,
        popup=get_height(end),
        tooltip="End Point",
    ).add_to(m)

    with pyinstrument.profile():
        path = compute_path(start, end)

    latlon_path = [convert_lv95_to_wgs84(loc) for loc in path]
    latlon_path = smooth_line(latlon_path)

    folium.PolyLine(latlon_path, color="blue").add_to(m)

    # Display the map
    folium_static(m)


if __name__ == "__main__":
    main()
