"use client";
import { LatLng, LatLngExpression, LatLngTuple } from "leaflet";
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import {
  LayerGroup,
  LayersControl,
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  WMSTileLayer,
  useMapEvents,
} from "react-leaflet";

const { BaseLayer, Overlay } = LayersControl; // Destructure BaseLayer and Overlay

interface MapProps {
  posix: LatLngExpression | LatLngTuple;
  zoom?: number;
}

const defaults = {
  zoom: 14,
};

interface ShortestPathProps {
  setLoading: (loading: boolean) => void;
}

function ShortestPath({ setLoading }: ShortestPathProps) {
  const [start, setStart] = useState<LatLng | null>(null);
  const [end, setEnd] = useState<LatLng | null>(null);
  const [shortestPath, setShortestPath] = useState<LatLngTuple[] | null>(null);

  useEffect(() => {
    if (start && end) {
      setLoading(true);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      fetch(`${apiUrl}/shortest-path`, {
        method: "POST",
        body: JSON.stringify({ start, end }),
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((res) => res.json())
        .then((data) => {
          setShortestPath(data);
          setLoading(false);
        });
    }
  }, [start, end, setLoading]);

  const map = useMapEvents({
    click(e) {
      if (start === null) {
        setStart(e.latlng);
      } else if (end === null) {
        setEnd(e.latlng);
      } else {
        setStart(e.latlng);
        setEnd(null);
        setShortestPath(null);
      }
    },
  });

  return (
    <LayerGroup>
      {start && (
        <Marker position={start}>
          <Popup>Start</Popup>
        </Marker>
      )}
      {shortestPath && <Polyline positions={shortestPath} />}
      {end && (
        <Marker position={end}>
          <Popup>End</Popup>
        </Marker>
      )}
    </LayerGroup>
  );
}

const Map = ({ posix, zoom = defaults.zoom }: MapProps) => {
  const [isLoading, setLoading] = useState(false);

  return (
    <div className="relative h-full w-full">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center z-[1000] dark:bg-gray-700 dark:bg-opacity-70 bg-white bg-opacity-70">
          <div>
            <svg
              aria-hidden="true"
              className="inline-block align-middle w-6 h-6 text-gray-200 animate-spin dark:text-gray-600 fill-gray-600 dark:fill-gray-300"
              viewBox="0 0 100 101"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                fill="currentColor"
              />
              <path
                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                fill="currentFill"
              />
            </svg>
            <span className="inline-block align-middle ml-5">
              Computing path...
            </span>
          </div>
        </div>
      )}
      <MapContainer
        center={posix}
        zoom={zoom}
        style={{ height: "100%", width: "100%" }}
      >
        <LayersControl position="topright">
          <BaseLayer checked name="Base Map Winter">
            <TileLayer
              attribution='&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>'
              url="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg"
            />
          </BaseLayer>
          <Overlay checked name="Categorical Avalanche Terrain">
            <TileLayer
              attribution='&copy; <a href="https://www.slf.ch/">SLF</a>'
              url="https://map.slf.ch/public/mapcache/wmts/1.0.0/ch.slf.terrainclassification-hybr/default/GoogleMapsCompatible/{z}/{y}/{x}.png"
              opacity={0.5}
            />
          </Overlay>
          <Overlay name="Ski routes">
            <WMSTileLayer
              url="https://wms.geo.admin.ch/"
              layers="ch.swisstopo-karto.skitouren"
              format="image/png"
              transparent={true}
              opacity={0.3}
              attribution='&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>'
            />
          </Overlay>
        </LayersControl>
        <ShortestPath setLoading={setLoading} />
      </MapContainer>
    </div>
  );
};

export default Map;
