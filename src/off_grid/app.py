import folium
import streamlit as st
from streamlit_folium import st_folium

from off_grid.pathfinding import compute_path
from off_grid.util import (
    convert_lv95_to_wgs84,
    convert_wgs84_to_lv95,
    smooth_line,
)


def initialize_session_state():
    """Initialize session state variables for map center, zoom, clicks, and objects."""
    defaults = {
        "click_history": [],
        "objects": [],
        "map_center": (46.802128, 9.833477),  # Davos
        "zoom_level": 12,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def create_map():
    """Create and return the base map with added tile layers and layer controls."""
    m = folium.Map(
        location=st.session_state.map_center, zoom_start=st.session_state.zoom_level
    )
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
    return m


def handle_click_event(map_data):
    """Handle click events to add markers and compute path between two points."""
    last_clicked = map_data.get("last_clicked")
    if last_clicked and (
        not st.session_state.click_history
        or last_clicked != st.session_state.click_history[-1]
    ):
        coords = last_clicked["lat"], last_clicked["lng"]

        st.session_state.click_history.append(coords)
        marker = folium.Marker(
            location=coords,
            tooltip="Start Point"
            if len(st.session_state.click_history) == 1
            else "End Point",
        )
        st.session_state.objects.append(marker)

        if len(st.session_state.click_history) == 2:
            compute_and_display_path()

        st.rerun()


def compute_and_display_path():
    """Compute path between two points, smooth it, and add it to the map if possible."""
    start, end = st.session_state.click_history
    s, e = convert_wgs84_to_lv95(start), convert_wgs84_to_lv95(end)
    path = compute_path(s, e)

    if path and len(path) > 1:
        latlon_path = [convert_lv95_to_wgs84(loc) for loc in path]
        latlon_path = smooth_line(latlon_path)
        st.session_state.objects.append(folium.PolyLine(latlon_path, color="blue"))
    else:
        st.warning("Couldn't find a path or path is too short.", icon="🐛")


def main():
    st.title("Pathfinding based on Classified Avalanche Terrain Map")

    # Initialize session state
    initialize_session_state()

    # Create map and render with existing markers and paths
    m = create_map()
    fg = folium.FeatureGroup(name="objects")
    for obj in st.session_state.objects:
        fg.add_child(obj)

    map_data = st_folium(
        m,
        center=st.session_state.map_center,
        zoom=st.session_state.zoom_level,
        key="map",
        feature_group_to_add=fg,
        use_container_width=True,
        height=500,
    )

    # Handle map click events
    handle_click_event(map_data)
    st.warning(st.session_state.click_history)


if __name__ == "__main__":
    main()
