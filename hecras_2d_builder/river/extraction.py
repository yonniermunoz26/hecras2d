from __future__ import annotations

from typing import Any

import numpy as np
from shapely.geometry import LineString, MultiLineString


def extract_stream_lines(stream_mask: np.ndarray, spacing: float = 1.0) -> list[LineString]:
    """Convert a stream mask into simplified LineStrings for downstream selection."""
    rows, cols = stream_mask.shape
    lines: list[LineString] = []
    coords: list[tuple[float, float]] = []
    for r in range(rows):
        for c in range(cols):
            if stream_mask[r, c]:
                coords.append((float(c * spacing), float(r * spacing)))
    if coords:
        lines.append(LineString(coords))
    return lines


def pick_main_channel(stream_lines: list[LineString]) -> LineString | None:
    if not stream_lines:
        return None
    return max(stream_lines, key=lambda line: line.length)
