from __future__ import annotations

from typing import Any

import numpy as np


def calculate_flow_direction(dem: np.ndarray) -> np.ndarray:
    """Compute a simple 8-direction flow field using steepest descent."""
    dem = np.asarray(dem, dtype=float)
    if dem.ndim != 2:
        raise ValueError("DEM must be a 2D array.")

    rows, cols = dem.shape
    directions = np.full(dem.shape, -1, dtype=int)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            center = dem[r, c]
            neighbors = []
            for rr in range(r - 1, r + 2):
                for cc in range(c - 1, c + 2):
                    if rr == r and cc == c:
                        continue
                    neighbor = dem[rr, cc]
                    if np.isfinite(neighbor) and neighbor < center:
                        neighbors.append((center - neighbor, rr, cc))
            if not neighbors:
                directions[r, c] = 0
                continue
            _, rr, cc = max(neighbors)
            directions[r, c] = _direction_code(r, c, rr, cc)
    return directions


def _direction_code(r0: int, c0: int, r1: int, c1: int) -> int:
    dr = r1 - r0
    dc = c1 - c0
    codes = {
        (-1, -1): 1,
        (-1, 0): 2,
        (-1, 1): 3,
        (0, -1): 4,
        (0, 1): 5,
        (1, -1): 6,
        (1, 0): 7,
        (1, 1): 8,
    }
    return codes.get((dr, dc), 0)


def calculate_flow_accumulation(dem: np.ndarray, flow_direction: np.ndarray | None = None) -> np.ndarray:
    """Estimate cumulative upstream flow from a raster DEM by summing all contributing cells."""
    dem = np.asarray(dem, dtype=float)
    if flow_direction is None:
        flow_direction = calculate_flow_direction(dem)

    rows, cols = dem.shape
    upstream: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for r in range(rows):
        for c in range(cols):
            if not np.isfinite(dem[r, c]):
                continue
            direction = flow_direction[r, c]
            if direction == 0:
                continue
            rr, cc = _move_one_cell(r, c, direction)
            if 0 <= rr < rows and 0 <= cc < cols:
                upstream.setdefault((rr, cc), []).append((r, c))

    accumulation = np.ones((rows, cols), dtype=float)
    for r, c in sorted([(rr, cc) for rr in range(rows) for cc in range(cols)], key=lambda pos: dem[pos[0], pos[1]], reverse=True):
        total = 1.0
        for rr, cc in upstream.get((r, c), []):
            total += accumulation[rr, cc]
        accumulation[r, c] = total
    return accumulation


def _move_one_cell(r: int, c: int, direction: int) -> tuple[int, int]:
    deltas = {
        1: (-1, -1),
        2: (-1, 0),
        3: (-1, 1),
        4: (0, -1),
        5: (0, 1),
        6: (1, -1),
        7: (1, 0),
        8: (1, 1),
    }
    dr, dc = deltas.get(direction, (0, 0))
    return r + dr, c + dc


def extract_streams_from_accumulation(flow_accumulation: np.ndarray, threshold: float) -> np.ndarray:
    """Return a boolean mask of stream cells above a threshold."""
    acc = np.asarray(flow_accumulation, dtype=float)
    return acc >= float(threshold)
