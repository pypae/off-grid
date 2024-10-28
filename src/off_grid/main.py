from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from off_grid.pathfinding import Location, compute_path
from off_grid.util import convert_lv95_to_wgs84, convert_wgs84_to_lv95, smooth_line

app = FastAPI()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LocationModel(BaseModel):
    lat: float
    lng: float


class PathRequest(BaseModel):
    start: LocationModel
    end: LocationModel


@app.post("/shortest-path")
async def get_path(body: PathRequest):
    s = convert_wgs84_to_lv95((body.start.lat, body.start.lng))
    e = convert_wgs84_to_lv95((body.end.lat, body.end.lng))
    path = compute_path(s, e)

    if path and len(path) > 1:
        latlon_path = [convert_lv95_to_wgs84(loc) for loc in path]
        latlon_path = smooth_line(latlon_path)
        return latlon_path
