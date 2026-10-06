from __future__ import annotations

from shapely.geometry import Polygon


def generate_2d_area(study_area: Polygon, margin_m: float = 25.0) -> Polygon:
    if study_area.is_empty:
        raise ValueError("Study area polygon is empty.")
    envelope = study_area.buffer(margin_m)
    if not envelope.is_valid:
        envelope = envelope.buffer(0)
    return envelope
