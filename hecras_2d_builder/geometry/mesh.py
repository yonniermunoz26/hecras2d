from __future__ import annotations

from typing import Any

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, box


def generate_mesh(area_polygon: Polygon, cell_size_m: float = 10.0) -> gpd.GeoDataFrame:
    if cell_size_m <= 0:
        raise ValueError("cell_size_m must be greater than zero.")
    if area_polygon.is_empty:
        raise ValueError("Area polygon is empty.")

    minx, miny, maxx, maxy = area_polygon.bounds
    cells: list[Polygon] = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            rect = box(x, y, x + cell_size_m, y + cell_size_m)
            if rect.intersects(area_polygon):
                clipped = rect.intersection(area_polygon)
                if clipped.geom_type == "Polygon" and clipped.is_valid and clipped.area > 0:
                    cells.append(clipped)
                elif clipped.geom_type == "MultiPolygon":
                    for part in clipped.geoms:
                        if part.area > 0:
                            cells.append(part)
            y += cell_size_m
        x += cell_size_m

    return gpd.GeoDataFrame(geometry=cells, crs="EPSG:32618")
