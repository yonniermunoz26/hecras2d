from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class DEMValidationResult:
    is_valid: bool
    warnings: list[str]
    stats: dict[str, float]


def validate_dem(dem: dict[str, Any]) -> DEMValidationResult:
    """Validate a DEM-like dictionary with basic checks."""
    warnings: list[str] = []
    array = np.asarray(dem.get("array", np.array([])), dtype=float)

    if array.size == 0:
        return DEMValidationResult(False, ["DEM is empty."], {})

    if array.ndim != 2:
        warnings.append("DEM must be a 2D array.")

    if dem.get("crs") in (None, ""):
        warnings.append("DEM CRS is missing. A projected CRS is recommended.")
    elif dem["crs"].startswith("EPSG:") is False:
        warnings.append("DEM CRS is not explicitly EPSG-based. Verify coordinate reference system.")

    resolution = float(dem.get("resolution", 0.0) or 0.0)
    if resolution <= 0:
        warnings.append("DEM resolution is invalid or missing.")

    nodata = dem.get("nodata")
    if nodata is not None:
        valid_mask = array != nodata
        nodata_fraction = 1.0 - (np.count_nonzero(valid_mask) / array.size)
    else:
        nodata_fraction = 0.0

    if nodata_fraction > 0.2:
        warnings.append("DEM has a large nodata fraction; review the raster before building the model.")

    min_elev = float(np.nanmin(array)) if array.size else float("nan")
    max_elev = float(np.nanmax(array)) if array.size else float("nan")
    stats = {
        "min": min_elev,
        "max": max_elev,
        "mean": float(np.nanmean(array)) if array.size else float("nan"),
        "nodata_fraction": float(nodata_fraction),
        "resolution": resolution,
        "shape": list(array.shape),
    }

    return DEMValidationResult(is_valid=len(warnings) == 0, warnings=warnings, stats=stats)
