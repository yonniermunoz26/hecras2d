from __future__ import annotations

import geopandas as gpd
from shapely.geometry import LineString


def generate_breaklines(centerline: LineString, buffer_distance: float = 0.0) -> gpd.GeoDataFrame:
    if centerline.is_empty:
        raise ValueError("Centerline is empty.")
    geometry = centerline if buffer_distance <= 0 else centerline.buffer(buffer_distance)
    return gpd.GeoDataFrame({"name": ["AUTO-GENERATED / NEEDS REVIEW"], "geometry": [geometry]}, crs="EPSG:32618")
