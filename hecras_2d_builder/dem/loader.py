from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

try:
    import rasterio
except Exception:  # pragma: no cover
    rasterio = None


def load_dem(path: str | Path) -> dict[str, Any]:
    """Load a DEM dataset from a GeoTIFF when rasterio is available."""
    dem_path = Path(path)
    if not dem_path.exists():
        raise FileNotFoundError(f"DEM file not found: {dem_path}")

    if rasterio is None:
        raise RuntimeError(
            "rasterio is required to read GeoTIFF DEM files. Install requirements first."
        )

    with rasterio.open(dem_path) as src:
        array = src.read(1)
        data = {
            "path": str(dem_path),
            "array": np.asarray(array, dtype=float),
            "crs": src.crs.to_string() if src.crs else None,
            "transform": src.transform,
            "nodata": src.nodata,
            "resolution": abs(src.res[0]),
            "shape": array.shape,
            "bounds": src.bounds,
        }
    return data
