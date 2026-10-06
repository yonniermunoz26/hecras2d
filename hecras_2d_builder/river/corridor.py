from __future__ import annotations

from shapely.geometry import LineString, Polygon


def generate_study_area(centerline: LineString, river_buffer_m: float = 500.0, upstream_extension_m: float = 300.0, downstream_extension_m: float = 400.0, lateral_margin_m: float = 200.0) -> Polygon:
    """Create a corridor polygon around a river centerline."""
    if centerline.is_empty:
        raise ValueError("The centerline is empty.")

    # Extend the line at both ends to account for upstream/downstream reach selection.
    coords = list(centerline.coords)
    if len(coords) < 2:
        return centerline.buffer(river_buffer_m, cap_style=1).buffer(0)

    start = coords[0]
    end = coords[-1]
    extended = [
        (start[0] - upstream_extension_m, start[1]),
        *coords,
        (end[0] + downstream_extension_m, end[1]),
    ]
    extended_line = LineString(extended)
    corridor = extended_line.buffer(river_buffer_m + lateral_margin_m, cap_style=1, join_style=1)
    return corridor
